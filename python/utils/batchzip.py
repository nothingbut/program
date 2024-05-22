import zipfile, os

txtroot = '/Volumes/transfer/Ebooks/知轩MT/'
ziproot = '/Volumes/transfer/Ebooks/zxcs/'

files = os.listdir(txtroot)
for file in files:
    if (file.endswith('.txt')):
        name = file[0:-4]
        with zipfile.ZipFile('%s%s.zip' % (ziproot, name), 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write('%s%s.txt' % (txtroot, name))
            print('%s%s.txt was backup' % (txtroot, name))