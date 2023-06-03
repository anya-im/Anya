import sqlite3
import struct
import marisa_trie
import numpy as np
from abc import ABCMeta


class Dictionary(metaclass=ABCMeta):
    def __init__(self, db_path="./anya-dic.db", vec_size=8, initialize=False):
        self._words_vec = None
        self._vec_size = vec_size
        self._conn = sqlite3.connect(db_path)
        self._cur = self._conn.cursor()
        self._db_path = db_path
        self._pos_len = 0

        if not initialize:
            self._cur.execute('SELECT count(*) FROM positions;')
            self._pos_len = self._cur.fetchone()[0]

            search_key = "_BOS"
            self._cur.execute('SELECT id FROM words WHERE name = ?;', (search_key,))
            self._wid_BOS = self._cur.fetchone()[0]
            self._is_update = False

            self._words, self._trie = self._build_db()

        self._pid_eye = np.eye(self.pos_len, dtype="float32")

    @property
    def wid_bos(self):
        return self._wid_BOS

    @property
    def single_vec_size(self):
        #return self.word_vec_size + self.pos_len + 1
        return self.word_vec_size + self.pos_len

    @property
    def input_vec_size(self):
        return self.single_vec_size

    def _vec_eye(self, wid):
        return self._pid_eye[(self._words[str(wid)]["pos"] - 1)]

    def _build_db(self):
        words = {}
        trie_key = []
        trie_val = []

        self._cur.execute('SELECT words.id, words.name, words.read, words.pos, cost.val, words.vec FROM words INNER JOIN cost ON words.id = cost.id;')
        for data in self._cur.fetchall():
            wid = str(data[0])
            words[wid] = {
                "name": data[1],
                "read": data[2],
                "pos": data[3],
                "cost": np.array([data[4]], dtype="float32"),
                "vec": np.array(struct.unpack('=%df' % self._vec_size, data[5]), dtype="float32")
            }
            trie_key.append(data[2])
            trie_val.append(wid.encode())

        trie = marisa_trie.BytesTrie(zip(trie_key, trie_val))
        return words, trie

    def wid2name(self, wid):
        return self._words[wid]["name"]

    def wid2vec(self, wid):
        return self._words[wid.decode()]["vec"]

    @staticmethod
    def _read_vec(vec_path):
        vec_dic = {}
        with open(vec_path, encoding='utf8') as f:
            line_header = True
            for line in f:
                if not line_header:
                    row = line.split(" ")
                    vec = np.array([float(row[1]), float(row[2]), float(row[3]), float(row[4])], dtype=np.float16)
                    vec_dic[row[0]] = struct.pack('=4f', *vec)
                line_header = False
        return vec_dic

    def commit(self):
        if self._is_update:
            self._cur.execute('commit;')
        self._is_update = False

    def close(self):
        self._cur.close()
        self._conn.close()

    @property
    def vec_size(self):
        return self.word_vec_size + self.pos_len

    @property
    def word_vec_size(self):
        return self._vec_size

    @property
    def pos_len(self):
        return self._pos_len

    def _insert_pid(self, grp_name, sub_name):
        self._cur.execute('SELECT id FROM positions_group where name = ?;', (grp_name,))
        pid = self._cur.fetchone()
        if pid is None:
            self._cur.execute('INSERT INTO positions_group(name) values(?);', (grp_name,))
            self._cur.execute('SELECT id FROM positions_group where name = ?;', (grp_name,))
            pid = self._cur.fetchone()

        self._cur.execute('INSERT INTO positions(group_id, sub_name) values(?, ?);', (pid[0], sub_name))
        self._is_update = True

    def _pid_from_name(self, grp_name, sub_name):
        search_sql_str = "SELECT T1.id from positions as T1 join " \
                         "positions_group as T2 on T1.group_id = T2.id where T2.name=? and T1.sub_name=?;"
        self._cur.execute(search_sql_str, (grp_name, sub_name))
        res = self._cur.fetchone()
        if res is not None:
            pos_id = res[0]

        else:
            # Oops. add new record
            self._insert_pid(grp_name, sub_name)

            # research
            self._cur.execute(search_sql_str, (grp_name, sub_name))
            res = self._cur.fetchone()
            pos_id = res[0]

        return pos_id

    def _insert_word(self, name, read, pos_id):
        if self._words_vec is not None and name in self._words_vec:
            vec = self._words_vec[name]
        else:
            vec_np = np.random.rand(self._vec_size)
            vec = struct.pack('=%df' % vec_np.size, *vec_np)
        self._cur.execute('INSERT INTO words(name, read, pos, vec) values(?, ?, ?, ?);',
                          (name, read, pos_id, vec))
        self._is_update = True

    def get_name(self, wid):
        self._cur.execute('SELECT name FROM words where id = ?;', (wid,))
        return self._cur.fetchone()[0]


class DictionaryConverter(Dictionary):
    def __init__(self, db_path="./anya-dic.db"):
        super().__init__(db_path)

    def get(self, wid):
        return np.concatenate([self._words[str(wid)]["vec"], self._pid_eye[(self._words[str(wid)]["pos"] - 1)]])
        #return np.concatenate([self._words[str(wid)]["vec"], self._words[str(wid)]["cost"], self._pid_eye[(self._words[str(wid)]["pos"] - 1)]])

    def cost(self, wid):
        return self._words[str(wid.decode())]["cost"]

    def get_dwords(self, wid_f, wid_s):
        return np.concatenate([self._words[str(wid_f)]["vec"],
                               self._vec_eye(wid_f),
                               self._words[str(wid_s)]["vec"],
                               self._vec_eye(wid_s)])

    def gets(self, ym):
        return self._trie[ym]
        #return [wid_b.encode() for wid_b in self._trie[ym]]

    def build_word_tree(self, in_text):
        word_set = [[] for _ in range(len(in_text))]
        for i in range(len(in_text)):
            for prefix in self._trie.prefixes(in_text[i:]):
                word_set[i+len(prefix)-1].append(prefix)
        return word_set
