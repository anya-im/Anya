# anya

## モデル、及び辞書ファイルのダウンロード
下記の場所からモデルファイル及び辞書ファイルをダウンロードしてください  
https://www.dropbox.com/sh/i6y5wqhdccb4kur/AAA-a733IiDASpQe9mQk4vUYa?dl=0

* anya.mdl
* anya-dic.db

## Install
```shell
python setup.py install
```

## Run
```shell
anya -m anya.mdl -d anya-dic.db
```

### from docker
```shell
docker run -d -p 30055:30055 -v $HOME/.local/share/anya:/opt/anya ghcr.io/anya-im/anya -m anya.mdl -d anya-dic.db
```

※ 起動方法は今後変わることが想定されます
