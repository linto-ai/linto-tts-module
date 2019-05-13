# -*- mode: python -*-

block_cipher = None


a = Analysis(['linto_tts/tts_client.py'],
             pathex=['/home/rbaraglia/repositories/linto/linto-tts-module'],
             binaries=[],
             datas=[('linto_tts/.env_default', '.'), 
                    ('linto_tts/mqtt_msg.json', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='tts_client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='linto_tts')
