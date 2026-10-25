"""Private six-golden transport; one fresh Node per check, never a result cache.

Only the fixed Rear drivers are supported. Each job has a fresh JS VM and cwd;
Sharp/native library state is shared within this check (cache disabled by every
original driver). This is not a general subprocess or VM sandbox replacement.
Python golden functions and all their output assertions remain authoritative.
"""
import base64
import json
import os
import selectors
import subprocess
import time
import types

DRIVER=r'''
const vm=require('vm'),readline=require('readline');
const lines=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
(async()=>{for await(const line of lines){const job=JSON.parse(line);let out=[],err=[],outN=0,errN=0,code=0,read=false;
process.chdir(job.cwd);
const stream=(chunks,iserr)=>({write(x,encoding,callback){const b=Buffer.from(x,typeof encoding==='string'?encoding:undefined);if(iserr){errN+=b.length;if(errN>131072)throw Error('stderr limit');}else{outN+=b.length;if(outN>1048576)throw Error('stdout limit');}chunks.push(b);if(typeof encoding==='function')encoding();if(typeof callback==='function')callback();return true;}});
const p={version:process.version,platform:process.platform,arch:process.arch,argv:[process.argv[0],job.sharp],stdout:stream(out,false),stderr:stream(err,true),exit(n){code=n;throw Error('exit '+n);}};
const req=n=>n==='fs'?{readFileSync(fd,encoding){if(fd!==0||encoding!=='utf8'||read)throw Error('unsupported read');read=true;return job.input;}}:require(n);
try{await vm.runInNewContext(job.driver,{require:req,process:p,Buffer},{timeout:30000});}catch(e){code=1;err=[Buffer.from(String(e).slice(0,131072))];}
process.stdout.write(JSON.stringify({out:Buffer.concat(out).toString('base64'),err:Buffer.concat(err).toString('base64'),code})+'\n');
}})().catch(e=>{process.stderr.write(String(e));process.exit(1)});
'''

_ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
_FAMILIES = ('rear_p7', 'rear39', 'rear1', 'rear281', 'rear_lobes')


def tool_environment():
    return dict(environment=dict(_ENV), families=_FAMILIES)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate golden transport field')
        result[key] = value
    return result


class _Batch:
    TimeoutExpired = subprocess.TimeoutExpired

    def __init__(self):
        self.proc = None
        self.started = time.monotonic()
        self.calls = 0

    def close(self):
        if self.proc is not None:
            proc, self.proc = self.proc, None
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            for stream in (proc.stdin, proc.stdout, proc.stderr):
                if stream is not None:
                    stream.close()

    def finish(self):
        """Require a clean worker exit, not merely a valid final response frame."""
        if self.proc is None or self.calls != 6:
            raise ValueError('Incomplete golden renderer transport')
        deadline = min(time.monotonic() + 30, self.started + 180)
        try:
            self.proc.stdin.close()
            self.proc.stdin = None
            with selectors.DefaultSelector() as sel:
                sel.register(self.proc.stdout, selectors.EVENT_READ)
                sel.register(self.proc.stderr, selectors.EVENT_READ)
                while sel.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(self.proc.args, 30)
                    events = sel.select(remaining)
                    if not events:
                        raise subprocess.TimeoutExpired(self.proc.args, 30)
                    for key, _ in events:
                        if os.read(key.fd, 65536):
                            raise ValueError('Trailing golden renderer transport output')
                        sel.unregister(key.fileobj)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(self.proc.args, 30)
            if self.proc.wait(timeout=remaining) != 0:
                raise ValueError('Golden renderer worker exited unsuccessfully')
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError('Golden renderer shutdown unavailable/timed out') from exc

    def run(self, args, **kw):
        if (not isinstance(args, list) or len(args) != 5 or
                args[1:3] != ['--max-old-space-size=128', '-e'] or
                not all(isinstance(x, str) for x in args) or
                set(kw) != {'input', 'stdout', 'stderr', 'cwd', 'env', 'timeout'} or
                kw['env'] != _ENV or kw['timeout'] != 30 or
                not isinstance(kw['input'], bytes)):
            raise ValueError('Unsupported golden renderer invocation')
        self.calls += 1
        if self.calls > 6:
            raise ValueError('Too many golden renderer jobs')
        deadline = min(time.monotonic() + 30, self.started + 180)
        payload = json.dumps(dict(driver=args[3], sharp=args[4],
                                  input=kw['input'].decode('utf8'), cwd=kw['cwd'])).encode() + b'\n'
        if len(payload) > 256 * 1024:
            raise ValueError('Oversize golden renderer request')
        if self.proc is None:
            self.node = args[0]
            self.proc = subprocess.Popen(
                [self.node, '--max-old-space-size=128', '-e', DRIVER],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=_ENV, cwd=kw['cwd'], bufsize=0)
            for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
                os.set_blocking(stream.fileno(), False)
        elif args[0] != self.node:
            raise ValueError('Golden renderer executable changed within check')
        data, diagnostic, written = bytearray(), bytearray(), 0
        with selectors.DefaultSelector() as sel:
            sel.register(self.proc.stdin, selectors.EVENT_WRITE, 'in')
            sel.register(self.proc.stdout, selectors.EVENT_READ, 'out')
            sel.register(self.proc.stderr, selectors.EVENT_READ, 'err')
            while b'\n' not in data:
                left = deadline - time.monotonic()
                if left <= 0:
                    raise subprocess.TimeoutExpired(args, 30)
                events = sel.select(left)
                if not events:
                    raise subprocess.TimeoutExpired(args, 30)
                for key, _ in events:
                    if key.data == 'in':
                        written += os.write(key.fd, payload[written:])
                        if written == len(payload):
                            sel.unregister(key.fileobj)
                    else:
                        chunk = os.read(key.fd, 65536)
                        if not chunk:
                            raise OSError('Golden renderer process ended')
                        target = data if key.data == 'out' else diagnostic
                        target.extend(chunk)
                        if len(target) > (1600000 if key.data == 'out' else 128 * 1024):
                            raise OSError('Golden renderer transport output limit')
        line, extra = bytes(data).split(b'\n', 1)
        if extra or diagnostic or written != len(payload):
            raise OSError('Unexpected golden renderer transport output')
        response = json.loads(line, object_pairs_hook=_unique)
        if (not isinstance(response, dict) or set(response) != {'out', 'err', 'code'} or
                type(response['code']) is not int or not 0 <= response['code'] <= 255 or
                type(response['out']) is not str or type(response['err']) is not str):
            raise ValueError('Invalid golden renderer response')
        out = base64.b64decode(response['out'], validate=True)
        err = base64.b64decode(response['err'], validate=True)
        if len(out) > 1024 * 1024 or len(err) > 128 * 1024:
            raise ValueError('Oversize golden renderer output')
        kw['stdout'].write(out)
        kw['stderr'].write(err)
        return subprocess.CompletedProcess(args, response['code'])


def _clone(function, namespace):
    copied = types.FunctionType(function.__code__, namespace, function.__name__,
                                function.__defaults__, function.__closure__)
    copied.__kwdefaults__ = function.__kwdefaults__
    return copied


def check_tools(modules):
    """Run unchanged Python checkers in order using one bounded lazy transport."""
    if tuple(m.__name__ for m in modules) != tuple('current_' + f + '_compatibility' for f in _FAMILIES):
        raise ValueError('Unexpected golden renderer families/order')
    batch = _Batch()
    try:
        for module in modules:
            render, checker = module.render, module.check_tool
            if (not isinstance(render, types.FunctionType) or
                    not isinstance(checker, types.FunctionType) or
                    render.__globals__ is not module.__dict__ or
                    checker.__globals__ is not module.__dict__):
                raise ValueError('Unsupported golden renderer callable binding')
            namespace = dict(module.__dict__)
            namespace['subprocess'] = batch
            namespace['render'] = _clone(render, namespace)
            _clone(checker, namespace)()
        if batch.calls != 6:
            raise ValueError('Incomplete golden renderer jobs')
        batch.finish()
    finally:
        batch.close()
