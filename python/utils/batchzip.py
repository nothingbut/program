import zipfile, os

orgroot = '/Users/shichang/Public/Books/beitai/zxcs/Volumes/transfer/Ebooks/知轩MT/'
desroot = '/Users/shichang/Public/Books/beitai/zxcs/'

files = os.listdir(orgroot)
for file in files:
    if (file.endswith('.txt')):
        name = file[0:-4]
        print(name)
        with zipfile.ZipFile('%s%s.zip' % (desroot, name), 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(filename='%s%s.txt' % (orgroot, name),arcname='%s.txt' % name)
            print('done %s' % name)
'''
files = os.listdir(orgroot)
for filename in files:
    if (filename.endswith('.zip')):
        with zipfile.ZipFile('%s%s' % (orgroot, filename)) as zf:
            zf.extractall(path=desroot)
'''
