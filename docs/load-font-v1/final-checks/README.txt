All raw final log bytes are retained losslessly as deterministic gzip files.
RECEIPT.json pins the original uncompressed bytes. The private projection
runner is copied for audit; its original runnable location is the sibling
load-font-final-checks-20261013 directory in the durable final package. It
never edits production/historical files and does not launch the engine.
