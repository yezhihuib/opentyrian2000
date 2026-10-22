#!/usr/bin/env python3
'Fresh loader and whole-string oracle, not recovered historical tests.'
if __name__ != "__main__":
    from cli_test_support import cli_suite

    def load_tests(loader, tests, pattern):
        return cli_suite(__file__)
else:
    #!/usr/bin/env python3
    """Fresh loader and whole-string oracle, not recovered historical tests."""
    import ctypes, hashlib, json, os, pathlib, random, shutil, struct, subprocess, sys
    from PIL import Image,ImageDraw,ImageFont
    ROOT=pathlib.Path(__file__).resolve().parents[1]
    OUT=pathlib.Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
    ASSETS=ROOT/'assets/hd/shared-menu-runs-v1'
    from cli_test_support import sdl2_cflags
    flags=sdl2_cflags()
    lib=OUT/'reconstructed-menu-loader.so'
    subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-O2','-shared','-fPIC',*flags,'-I'+str(ROOT/'src'),str(ROOT/'src/common_menu_runs.c'),str(ROOT/'tests/reconstructed_menu_runs_adapter.c'),'-o',str(lib)],check=True)
    l=ctypes.CDLL(str(lib));C=ctypes
    for name,args,result in [('common_menu_runs_set_directory',[C.c_char_p],C.c_bool),('common_menu_runs_load',[C.c_int],C.c_bool),('common_menu_runs_ready',[C.c_int],C.c_bool),('common_menu_runs_count',[C.c_int],C.c_uint),('common_menu_runs_generation',[C.c_int],C.c_uint64),('common_menu_numeric_runs_load',[],C.c_bool),('common_menu_numeric_runs_ready',[],C.c_bool),('reconstructed_numeric_dump',[C.c_char_p,C.POINTER(C.c_uint8),C.c_uint,C.POINTER(C.c_int)],C.c_int)]:
     f=getattr(l,name);f.argtypes=args;f.restype=result
    assert l.common_menu_runs_set_directory(os.fsencode(ASSETS))
    counts=[16,7,7,9,19,113]
    for family,count in enumerate(counts):assert l.common_menu_runs_load(family) and l.common_menu_runs_count(family)==count
    assert l.common_menu_numeric_runs_load()
    # Every family can retire without poisoning another, including numeric.
    for family in range(6):
     before=l.common_menu_runs_generation(family);l.common_menu_runs_shutdown(family)
     assert not l.common_menu_runs_ready(family) and l.common_menu_runs_generation(family)!=before
     assert all(l.common_menu_runs_ready(j) for j in range(6) if j!=family) and l.common_menu_numeric_runs_ready()
     assert l.common_menu_runs_load(family)
    font=ImageFont.truetype(str(ASSETS/'fonts/osifont.ttf'),128,layout_engine=ImageFont.Layout.RAQM)
    rng=random.Random(0x52465233)
    texts=['0','1','-1','-2147483648','2147483647','4294967295','18446744073709551615','Cost: 0','Cost: 65535']
    texts += [str(rng.randrange(-2**31,2**64)) for _ in range(500)]
    texts += ['Cost: '+str(rng.randrange(65536)) for _ in range(500)]
    buf=(C.c_uint8*20000)();metrics=(C.c_int*5)();pixels=0
    for text in texts:
     n=l.reconstructed_numeric_dump(text.encode(),buf,len(buf),metrics);assert n>0,text
     im=Image.new('L',(2048,160));ImageDraw.Draw(im).text((128,96),text,font=font,anchor='ls',fill=255)
     im=im.resize((512,40),Image.Resampling.BOX);bbox=im.getbbox();expected=im.crop(bbox)
     assert list(metrics)==[bbox[0]-32,bbox[1],expected.width,expected.height,round(font.getlength(text)*64)],(text,list(metrics),bbox)
     assert bytes(buf[:n])==expected.tobytes(),text;pixels+=n
    invalid=['','-','Cost: ','Cost: -1','-0','00','01','+1',' 1','1 ','1-2','1.0','Cost: 01','Cost: 65535x','x','9'*21]
    for text in invalid:assert l.reconstructed_numeric_dump(text.encode(),buf,len(buf),metrics)<0,text
    # One mutable generated fixture, restored after each injected failure.
    fixture=OUT/'fixture';fixture.mkdir(exist_ok=True)
    for p in ASSETS.glob('*.rfr'):shutil.copyfile(p,fixture/p.name)
    shutil.copyfile(ASSETS/'numeric-runs-v1.nfr',fixture/'numeric-runs-v1.nfr')
    files=sorted(fixture.glob('*.rfr'));negatives=0
    for p in files:
     raw=p.read_bytes();family=struct.unpack_from('<I',raw,36)[0]
     # The exact family comes from filename prefixes, not a production permission.
     family=next(i for i,prefix in enumerate(['esc-','main-','shop-','category-','product-','names-']) if p.name.startswith(prefix))
     for offset in [0,4,8,12,16,20,24,28,32,36,40,48,56,64,len(raw)-1]:
      data=bytearray(raw);data[offset]^=1;p.write_bytes(data)
      assert l.common_menu_runs_set_directory(None);assert l.common_menu_runs_set_directory(os.fsencode(fixture))
      assert not l.common_menu_runs_load(family),(p.name,offset)
      assert all(l.common_menu_runs_load(j) for j in range(6) if j!=family)
      assert l.common_menu_numeric_runs_load();p.write_bytes(raw);negatives+=1
    p=fixture/'numeric-runs-v1.nfr';raw=p.read_bytes()
    for offset in list(range(64))+[64,len(raw)-1]:
     b=bytearray(raw);b[offset]^=1;p.write_bytes(b);l.common_menu_runs_set_directory(None);l.common_menu_runs_set_directory(os.fsencode(fixture))
     assert not l.common_menu_numeric_runs_load();assert all(l.common_menu_runs_load(i) for i in range(6));p.write_bytes(raw);negatives+=1
    assert not l.common_menu_runs_set_directory(b'x'*1024)
    assert not any(l.common_menu_runs_ready(i) for i in range(6)) and not l.common_menu_numeric_runs_ready()
    assert not l.common_menu_runs_load(-1) and not l.common_menu_runs_load(6)
    receipt={'status':'PASS','whole_string_raqm_cases':len(texts),'independent_alpha_pixels':pixels,'invalid_canonical_strings':len(invalid),'resource_mutation_negatives':negatives,'families':counts,'numeric_sha256':hashlib.sha256(raw).hexdigest(),'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/common_menu_runs.c',ROOT/'src/common_menu_runs.h',pathlib.Path(__file__),ROOT/'tests/reconstructed_menu_runs_adapter.c']},'limits':'Loader and raster oracle only. No native menu semantic admission or gameplay acceptance.'}
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
