from datetime import datetime
import hashlib
import json
import socket
import shutil
import uuid
import os
import glob
# import random

####################
# トランザクションクラス
####################
class Transaction:
    # blockchainの初期化関数
    def __init__(self):
        print("トランザクションが発行、または受信しました。")

    # 受け取ったトランザクションの処理
    def recvTX(self):
        print("トランザクションを受信しました。")
        # 受け取ったトランザクションが`./data/.transaciton`にあるか
        # トランザクションがあったら処理を終了
        # 受け取ったトランザクションがなかったら`./data/transaction`に保存

    # 出席状況を示す変数`status`を引数としてトランザクションを生成する
    def createTX(self, status):
        # 出席者の名前の作成
        with open('info.json', 'r') as file:
            info_json = json.load(file)
        myName = info_json["name"]
        # タイムスタンプの作成
        now = datetime.now()
        timestamp = int(now.timestamp())
        # トランザクションの作成
        newTX = {
            "name": myName,
            "timestamp": timestamp,
            "status": status
        }
        # JSONファイルへの書き込み
        json_path = './data/transaction/' + str(uuid.uuid4()) + '.json'
        with open(json_path, 'w') as json_path:
            json.dump(newTX, json_path, indent=2)
        
        # 作成したjsonファイルを返す
        return newTX

####################
# ブロッククラス
####################
class Block:
    def __init__(self):
        print("ブロックが生成、または受信されました。\n")
    
    def recvBL(self):
        print("ブロックを受信しました。\n")
    
    def calculate_merkle(self):
        directory_path = "./data/transaction"
        # ディレクトリ内のJSONファイルのパスを取得
        json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        # JSONファイルのパスとtimestampの値を格納するリスト
        files_with_timestamp = []
        # ディレクトリ内のJSONファイルからtimestampの値を取得
        for json_file in json_files:
            file_path = os.path.join(directory_path, json_file)
            with open(file_path, 'r') as f:
                data = json.load(f)
                timestamp_value = data.get('timestamp')
                if timestamp_value is not None:
                    files_with_timestamp.append((file_path, timestamp_value))

        # timestampの値が小さい順にソート
        sorted_files = sorted(files_with_timestamp, key=lambda x: x[1])
        # 最初の8つのファイルの中身を文字列型の配列に格納
        file_contents = []
        for file_path, _ in sorted_files[:8]:
            with open(file_path, 'r') as f:
                content = f.read()
                file_contents.append(content)

        # マークルルートを計算
        hashed_values = [hashlib.sha256(data.encode('utf-8')).hexdigest() for data in file_contents]
        while len(hashed_values) > 1:
            temp = []
            for i in range(0, len(hashed_values), 2):
                # 2つのハッシュを連結してハッシュ化
                combined_hash = hashlib.sha256((hashed_values[i] + hashed_values[i + 1]).encode('utf-8')).hexdigest()
                temp.append(combined_hash)
            # 新しいハッシュリストを使用してループを続行
            hashed_values = temp
        merkle_root = hashed_values[0]
        return merkle_root

    def createBL(self): 
        # マークルルートの作成
        merkle = self.calculate_merkle()
        # タイムスタンプの作成
        now = datetime.now()
        timestamp = int(now.timestamp())

        # ブロックチェーン最後のハッシュの取得
        prevHash = ""
        # ノンス値の作成
        # nonce = random.randomint(1, 1000000)
        nonce = "none"
        # ブロックの作成
        newBL = {
            "prevHash": prevHash,
            "hash": merkle,
            "timestamp": timestamp,
            "nonce": nonce
        }
        # JSONファイルへの書き込み
        block_path = './data/block/' + str(uuid.uuid4()) + '.json'
        with open(block_path, 'w') as json_file:
            json.dump(newBL, json_file, indent=2)

####################
# ブロックチェーンクラス
####################
class Blockchain:
    def __init__(self):
        print("ブロックチェーンが更新されます。\n")
        
    def recvBC(self):
        print("ブロックチェーンを受信しました。\n")

    # ブロックプール内から一番小さいタイムスタンプのブロックを取得
    def setNewBL(self, Blockfolder):
        # フォルダ内のJSONファイルの一覧を取得
        json_files = [f for f in os.listdir(Blockfolder) if f.endswith('.json')]
        min_timestamp = 0
        min_timestamp_file_path = None

        for json_file in json_files:
            file_path = os.path.join(Blockfolder, json_file)

            # JSONファイルを読み込んでtimestampを取得
            with open(file_path, 'r') as f:
                data = json.load(f)
                timestamp = data.get('timestamp', float('inf'))
                if timestamp < min_timestamp:
                    min_timestamp = timestamp
                    min_timestamp_file_path = file_path

        return min_timestamp_file_path

    # ブロックチェーンにブロックを追加する関数
    def addtoBC(self, BCjson, BLFpath):
        # タイムスタンプが小さいブロックを取得
        BLpath = self.setNewBL(BLFpath)
        # 新しいブロックのindexの作成
        with open(BCpath, 'r') as file:
            BCjson = json.load(file)
        lastID = BCjson[-1]['index']
        nextID = lastID + 1
        # 新しいブロックのjsonを作成
        with open(BLpath, "r", encoding="utf-8") as file:
            newBC_json = json.load(file)
        # 追加するブロックの作成と更新
        newBL = {
            'index': nextID,
            'block': newBC_json
        }
        BCjson.append(newBL)
        # JSONファイルの読み込み
        with open(BCpath, 'r') as file:
            # ファイルを書き込みモードで開いてJSONデータを書き込む
            with open(BCpath, 'w') as write_file:
                json.dump(BCjson, write_file, indent=2)

        # 追加したブロックを別のフォルダに移動する
        BLmoveto = "./data/.block"
        shutil.move(BLpath, BLmoveto)

####################
# main関数
####################
if __name__ == "__main__":

    #####################
    # 出席システムの初期設定
    #####################
    # info.jsonファイルを読み込む
    with open('info.json', 'r') as file:
        info_json = json.load(file)
    # 変数にデータを格納
    myName = info_json["name"]
    HOST = info_json["HOST"]
    CLIENT = info_json["CLIENT"]
    PORT = info_json["PORT"]
    # ソケットの作成とバインド
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST,PORT))
    # 出席トランザクションの作成とブロードキャスト
    sampleTX = Transaction()
    newTX = sampleTX.createTX(True)
    sock.sendto(newTX, (CLIENT, PORT))

    #####################
    # ブロックチェーンに関するプログラム
    #####################
    # ブロックチェーンの読み込み
    BCpath = './data/blockchain/blockchain.json'
    with open(BCpath, 'r') as json_file:
        BCjson = json.load(json_file)
    # フォルダ内のファイルを取得
    BLFpath = './data/block'

    ######################
    # 常時実行プログラム
    ######################
    while True:
        ################################
        # 8つ以上のTXがあった場合、ブロックを作成
        ################################
        TXfiles = glob.glob(os.path.join("./data", '*.json'))
        TXcount = len(TXfiles)
        if TXcount >= 8:
            newBL = Block()
            newBL.createBL()
        
        ################################
        # ブロックチェーンにブロックを追加
        ################################
        # フォルダ内にファイルが存在するかチェック
        BLfolder = os.listdir(BLFpath)
        # ファイルが存在する場合、blockchainクラスのaddtoBC関数を実行
        if BLfolder:
            newBC = Blockchain()
            newBC.addtoBC(BCjson, BLFpath)        

        ################################
        # データをTX、BL、BCに仕分けして保存する
        ################################
        # ソケットを受け取り辞書にでコード
        recv_data, address = sock.recvfrom(4096)
        recv_json = json.loads(recv_data)
        # それぞれに存在するキーで仕分けしてそれぞれの処理を行う
        if 'status' in recv_json:
            recvTX = Transaction()
            recvTX.recvTX()
        elif 'hash' in recv_json:
            recvBL = Block()
            recvBL.recvBL()
        elif 'index' in recv_json:
            recvBC = Blockchain()
            recvBC.recvBC()
