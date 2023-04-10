import os
import csv

relation = {}

relation["a"] = ["ㄚ", "a", "ar", "aa", "ah"] 
relation["ai"] = ["ㄞ", "ai", "air", "ae", "ay"] 
relation["an"] = ["ㄢ", "an", "arn", "aan", "ann"] 
relation["ang"] = ["ㄤ", "ang", "arng", "aang", "anq"] 
relation["ao"] = ["ㄠ", "au", "aur", "ao", "aw"] 
relation["ba"] = ["ㄅㄚ", "ba", "bar", "baa", "bah"] 
relation["bai"] = ["ㄅㄞ", "bai", "bair", "bae", "bay"] 
relation["ban"] = ["ㄅㄢ", "ban", "barn", "baan", "bann"] 
relation["bang"] = ["ㄅㄤ", "bang", "barng", "baang", "banq"] 
relation["bao"] = ["ㄅㄠ", "bau", "baur", "bao", "baw"] 
relation["bei"] = ["ㄅㄟ", "bei", "beir", "beei", "bey"] 
relation["ben"] = ["ㄅㄣ", "ben", "bern", "been", "benn"] 
relation["beng"] = ["ㄅㄥ", "beng", "berng", "beeng", "benq"] 
relation["bi"] = ["ㄅㄧ", "bi", "byi", "bii", "bih"] 
relation["bian"] = ["ㄅㄧㄢ", "bian", "byan", "bean", "biann"] 
relation["biao"] = ["ㄅㄧㄠ", "biau", "byau", "beau", "biaw"] 
relation["bie"] = ["ㄅㄧㄝ", "bie", "bye", "biee", "bieh"] 
relation["bin"] = ["ㄅㄧㄣ", "bin", "byn", "biin", "binn"] 
relation["bing"] = ["ㄅㄧㄥ", "bing", "byng", "biing", "binq"] 
relation["bo"] = ["ㄅㄛ", "bo", "bor", "boo", "boh"] 
relation["bu"] = ["ㄅㄨ", "bu", "bwu", "buu", "buh"] 
relation["cha"] = ["ㄔㄚ", "cha", "char", "chaa", "chah"] 
relation["chai"] = ["ㄔㄞ", "chai", "chair", "chae", "chay"] 
relation["chan"] = ["ㄔㄢ", "chan", "charn", "chaan", "chann"] 
relation["chang"] = ["ㄔㄤ", "chang", "charng", "chaang", "chanq"] 
relation["chao"] = ["ㄔㄠ", "chau", "chaur", "chao", "chaw"] 
relation["che"] = ["ㄔㄜ", "che", "cher", "chee", "cheh"] 
relation["chen"] = ["ㄔㄣ", "chen", "chern", "cheen", "chenn"] 
relation["cheng"] = ["ㄔㄥ", "cheng", "cherng", "cheeng", "chenq"] 
relation["qi"] = ["ㄑㄧ", "chi", "chyi", "chii", "chih"] 
relation["qia"] = ["ㄑㄧㄚ", "chia", "chya", "chea", "chiah"] 
relation["qian"] = ["ㄑㄧㄢ", "chian", "chyan", "chean", "chiann"] 
relation["qiang"] = ["ㄑㄧㄤ", "chiang", "chyang", "cheang", "chianq"] 
relation["qiao"] = ["ㄑㄧㄠ", "chiau", "chyau", "cheau", "chiaw"] 
relation["qie"] = ["ㄑㄧㄝ", "chie", "chye", "chiee", "chieh"] 
relation["qin"] = ["ㄑㄧㄣ", "chin", "chyn", "chiin", "chinn"] 
relation["qing"] = ["ㄑㄧㄥ", "ching", "chyng", "chiing", "chinq"] 
relation["qiong"] = ["ㄑㄩㄥ", "chiong", "chyong", "cheong", "chionq"] 
relation["qiu"] = ["ㄑㄧㄡ", "chiou", "chyou", "cheou", "chiow"] 
relation["qu"] = ["ㄑㄩ", "chiu", "chyu", "cheu", "chiuh"] 
relation["quan"] = ["ㄑㄩㄢ", "chiuan", "chyuan", "cheuan", "chiuann"] 
relation["que"] = ["ㄑㄩㄝ", "chiue", "chyue", "cheue", "chiueh"] 
relation["qun"] = ["ㄑㄩㄣ", "chiun", "chyun", "cheun", "chiunn"] 
relation["chong"] = ["ㄔㄨㄥ", "chong", "chorng", "choong", "chonq"] 
relation["chou"] = ["ㄔㄡ", "chou", "chour", "choou", "chow"] 
relation["chu"] = ["ㄔㄨ", "chu", "chwu", "chuu", "chuh"] 
relation["chua"] = ["ㄔㄨㄚ", "chua", "chuar", "chuaa", "chuah"] 
relation["chuai"] = ["ㄔㄨㄞ", "chuai", "chwai", "choai", "chuay"] 
relation["chuan"] = ["ㄔㄨㄢ", "chuan", "chwan", "choan", "chuann"] 
relation["chuang"] = ["ㄔㄨㄤ", "chuang", "chwang", "choang", "chuanq"] 
relation["chui"] = ["ㄔㄨㄟ", "chuei", "chwei", "choei", "chuey"] 
relation["chun"] = ["ㄔㄨㄣ", "chuen", "chwen", "choen", "chuenn"] 
relation["chuo"] = ["ㄔㄨㄛ", "chuo", "chwo", "chuoo", "chuoh"] 
relation["chi"] = ["ㄔ", "chy", "chyr", "chyy", "chyh"] 
relation["da"] = ["ㄉㄚ", "da", "dar", "daa", "dah"] 
relation["dai"] = ["ㄉㄞ", "dai", "dair", "dae", "day"] 
relation["dan"] = ["ㄉㄢ", "dan", "darn", "daan", "dann"] 
relation["dang"] = ["ㄉㄤ", "dang", "darng", "daang", "danq"] 
relation["dao"] = ["ㄉㄠ", "dau", "daur", "dao", "daw"] 
relation["de"] = ["ㄉㄜ", "de", "der", "dee", "deh"] 
relation["dei"] = ["ㄉㄟ", "dei", "deir", "deei", "dey"] 
relation["den"] = ["ㄉㄣ", "den", "dern", "deen", "denn"] 
relation["deng"] = ["ㄉㄥ", "deng", "derng", "deeng", "denq"] 
relation["di"] = ["ㄉㄧ", "di", "dyi", "dii", "dih"] 
relation["dian"] = ["ㄉㄧㄢ", "dian", "dyan", "dean", "diann"] 
relation["diang"] = ["ㄉㄧㄤ", "diang", "dyang", "deang", "dianq"] 
relation["diao"] = ["ㄉㄧㄠ", "diau", "dyau", "deau", "diaw"] 
relation["die"] = ["ㄉㄧㄝ", "die", "dye", "diee", "dieh"] 
relation["ding"] = ["ㄉㄧㄥ", "ding", "dyng", "diing", "dinq"] 
relation["diu"] = ["ㄉㄧㄡ", "diou", "dyou", "deou", "diow"] 
relation["dong"] = ["ㄉㄨㄥ", "dong", "dorng", "doong", "donq"] 
relation["dou"] = ["ㄉㄡ", "dou", "dour", "doou", "dow"] 
relation["du"] = ["ㄉㄨ", "du", "dwu", "duu", "duh"] 
relation["duan"] = ["ㄉㄨㄢ", "duan", "dwan", "doan", "duann"] 
relation["dui"] = ["ㄉㄨㄟ", "duei", "dwei", "doei", "duey"] 
relation["dun"] = ["ㄉㄨㄣ", "duen", "dwen", "doen", "duenn"] 
relation["duo"] = ["ㄉㄨㄛ", "duo", "dwo", "duoo", "duoh"] 
relation["e"] = ["ㄜ", "e", "er", "ee", "eh"] 
relation["ei"] = ["ㄟ", "ei", "eir", "eei", "ey"] 
relation["er"] = ["ㄦ", "el", "erl", "eel", "ell"] 
relation["en"] = ["ㄣ", "en", "ern", "een", "enn"] 
relation["fa"] = ["ㄈㄚ", "fa", "far", "faa", "fah"] 
relation["fan"] = ["ㄈㄢ", "fan", "farn", "faan", "fann"] 
relation["fang"] = ["ㄈㄤ", "fang", "farng", "faang", "fanq"] 
relation["fei"] = ["ㄈㄟ", "fei", "feir", "feei", "fey"] 
relation["fen"] = ["ㄈㄣ", "fen", "fern", "feen", "fenn"] 
relation["feng"] = ["ㄈㄥ", "feng", "ferng", "feeng", "fenq"] 
relation["fo"] = ["ㄈㄛ", "fo", "for", "foo", "foh"] 
relation["fou"] = ["ㄈㄡ", "fou", "four", "foou", "fow"] 
relation["fu"] = ["ㄈㄨ", "fu", "fwu", "fuu", "fuh"] 
relation["ga"] = ["ㄍㄚ", "ga", "gar", "gaa", "gah"] 
relation["gai"] = ["ㄍㄞ", "gai", "gair", "gae", "gay"] 
relation["gan"] = ["ㄍㄢ", "gan", "garn", "gaan", "gann"] 
relation["gang"] = ["ㄍㄤ", "gang", "garng", "gaang", "ganq"] 
relation["gao"] = ["ㄍㄠ", "gau", "gaur", "gao", "gaw"] 
relation["ge"] = ["ㄍㄜ", "ge", "ger", "gee", "geh"] 
relation["gei"] = ["ㄍㄟ", "gei", "geir", "geei", "gey"] 
relation["gen"] = ["ㄍㄣ", "gen", "gern", "geen", "genn"] 
relation["geng"] = ["ㄍㄥ", "geng", "gerng", "geeng", "genq"] 
relation["gong"] = ["ㄍㄨㄥ", "gong", "gorng", "goong", "gonq"] 
relation["gou"] = ["ㄍㄡ", "gou", "gour", "goou", "gow"] 
relation["gu"] = ["ㄍㄨ", "gu", "gwu", "guu", "guh"] 
relation["gua"] = ["ㄍㄨㄚ", "gua", "gwa", "goa", "guah"] 
relation["guai"] = ["ㄍㄨㄞ", "guai", "gwai", "goai", "guay"] 
relation["guan"] = ["ㄍㄨㄢ", "guan", "gwan", "goan", "guann"] 
relation["guang"] = ["ㄍㄨㄤ", "guang", "gwang", "goang", "guanq"] 
relation["gui"] = ["ㄍㄨㄟ", "guei", "gwei", "goei", "guey"] 
relation["gun"] = ["ㄍㄨㄣ", "guen", "gwen", "goen", "guenn"] 
relation["guo"] = ["ㄍㄨㄛ", "guo", "gwo", "guoo", "guoh"] 
relation["ha"] = ["ㄏㄚ", "ha", "har", "haa", "hah"] 
relation["hai"] = ["ㄏㄞ", "hai", "hair", "hae", "hay"] 
relation["han"] = ["ㄏㄢ", "han", "harn", "haan", "hann"] 
relation["hang"] = ["ㄏㄤ", "hang", "harng", "haang", "hanq"] 
relation["hao"] = ["ㄏㄠ", "hau", "haur", "hao", "haw"] 
relation["he"] = ["ㄏㄜ", "he", "her", "hee", "heh"] 
relation["hei"] = ["ㄏㄟ", "hei", "heir", "heei", "hey"] 
relation["hen"] = ["ㄏㄣ", "hen", "hern", "heen", "henn"] 
relation["heng"] = ["ㄏㄥ", "heng", "herng", "heeng", "henq"] 
relation["hong"] = ["ㄏㄨㄥ", "hong", "horng", "hoong", "honq"] 
relation["hou"] = ["ㄏㄡ", "hou", "hour", "hoou", "how"] 
relation["hu"] = ["ㄏㄨ", "hu", "hwu", "huu", "huh"] 
relation["hua"] = ["ㄏㄨㄚ", "hua", "hwa", "hoa", "huah"] 
relation["huai"] = ["ㄏㄨㄞ", "huai", "hwai", "hoai", "huay"] 
relation["huan"] = ["ㄏㄨㄢ", "huan", "hwan", "hoan", "huann"] 
relation["huang"] = ["ㄏㄨㄤ", "huang", "hwang", "hoang", "huanq"] 
relation["hui"] = ["ㄏㄨㄟ", "huei", "hwei", "hoei", "huey"] 
relation["hun"] = ["ㄏㄨㄣ", "huen", "hwen", "hoen", "huenn"] 
relation["huo"] = ["ㄏㄨㄛ", "huo", "hwo", "huoo", "huoh"] 
relation["yi"] = ["ㄧ", "i", "yi", "yii", "yih"] 
relation["ya"] = ["ㄧㄚ", "ia", "ya", "yea", "yah"] 
relation["yan"] = ["ㄧㄢ", "ian", "yan", "yean", "yann"] 
relation["yang"] = ["ㄧㄤ", "iang", "yang", "yeang", "yanq"] 
relation["yao"] = ["ㄧㄠ", "iau", "yau", "yeau", "yaw"] 
relation["ye"] = ["ㄧㄝ", "ie", "ye", "yee", "yeh"] 
relation["yin"] = ["ㄧㄣ", "in", "yn", "yiin", "yinn"] 
relation["ying"] = ["ㄧㄥ", "ing", "yng", "yiing", "yinq"] 
relation["yong"] = ["ㄩㄥ", "iong", "yong", "yeong", "yonq"] 
relation["you"] = ["ㄧㄡ", "iou", "you", "yeou", "yow"] 
relation["yu"] = ["ㄩ", "iu", "yu", "yeu", "yuh"] 
relation["yuan"] = ["ㄩㄢ", "iuan", "yuan", "yeuan", "yuann"] 
relation["yue"] = ["ㄩㄝ", "iue", "yue", "yeue", "yueh"] 
relation["yun"] = ["ㄩㄣ", "iun", "yun", "yeun", "yunn"] 
relation["zha"] = ["ㄓㄚ", "ja", "jar", "jaa", "jah"] 
relation["zhai"] = ["ㄓㄞ", "jai", "jair", "jae", "jay"] 
relation["zhan"] = ["ㄓㄢ", "jan", "jarn", "jaan", "jann"] 
relation["zhang"] = ["ㄓㄤ", "jang", "jarng", "jaang", "janq"] 
relation["zhao"] = ["ㄓㄠ", "jau", "jaur", "jao", "jaw"] 
relation["zhe"] = ["ㄓㄜ", "je", "jer", "jee", "jeh"] 
relation["zhei"] = ["ㄓㄟ", "jei", "jeir", "jeei", "jey"] 
relation["zhen"] = ["ㄓㄣ", "jen", "jern", "jeen", "jenn"] 
relation["zheng"] = ["ㄓㄥ", "jeng", "jerng", "jeeng", "jenq"] 
relation["ji"] = ["ㄐㄧ", "ji", "jyi", "jii", "jih"] 
relation["jia"] = ["ㄐㄧㄚ", "jia", "jya", "jea", "jiah"] 
relation["jian"] = ["ㄐㄧㄢ", "jian", "jyan", "jean", "jiann"] 
relation["jiang"] = ["ㄐㄧㄤ", "jiang", "jyang", "jeang", "jianq"] 
relation["jiao"] = ["ㄐㄧㄠ", "jiau", "jyau", "jeau", "jiaw"] 
relation["jie"] = ["ㄐㄧㄝ", "jie", "jye", "jiee", "jieh"] 
relation["jin"] = ["ㄐㄧㄣ", "jin", "jyn", "jiin", "jinn"] 
relation["jing"] = ["ㄐㄧㄥ", "jing", "jyng", "jiing", "jinq"] 
relation["jiong"] = ["ㄐㄩㄥ", "jiong", "jyong", "jeong", "jionq"] 
relation["jiu"] = ["ㄐㄧㄡ", "jiou", "jyou", "jeou", "jiow"] 
relation["ju"] = ["ㄐㄩ", "jiu", "jyu", "jeu", "jiuh"] 
relation["juan"] = ["ㄐㄩㄢ", "jiuan", "jyuan", "jeuan", "jiuann"] 
relation["jue"] = ["ㄐㄩㄝ", "jiue", "jyue", "jeue", "jiueh"] 
relation["jun"] = ["ㄐㄩㄣ", "jiun", "jyun", "jeun", "jiunn"] 
relation["zhong"] = ["ㄓㄨㄥ", "jong", "jorng", "joong", "jonq"] 
relation["zhou"] = ["ㄓㄡ", "jou", "jour", "joou", "jow"] 
relation["zhu"] = ["ㄓㄨ", "ju", "jwu", "juu", "juh"] 
relation["zhua"] = ["ㄓㄨㄚ", "jua", "jwa", "joa", "juah"] 
relation["zhuai"] = ["ㄓㄨㄞ", "juai", "jwai", "joai", "juay"] 
relation["zhuan"] = ["ㄓㄨㄢ", "juan", "jwan", "joan", "juann"] 
relation["zhuang"] = ["ㄓㄨㄤ", "juang", "jwang", "joang", "juanq"] 
relation["zhui"] = ["ㄓㄨㄟ", "juei", "jwei", "joei", "juey"] 
relation["zhun"] = ["ㄓㄨㄣ", "juen", "jwen", "joen", "juenn"] 
relation["zhuo"] = ["ㄓㄨㄛ", "juo", "jwo", "juoo", "juoh"] 
relation["zhi"] = ["ㄓ", "jy", "jyr", "jyy", "jyh"] 
relation["ka"] = ["ㄎㄚ", "ka", "kar", "kaa", "kah"] 
relation["kai"] = ["ㄎㄞ", "kai", "kair", "kae", "kay"] 
relation["kan"] = ["ㄎㄢ", "kan", "karn", "kaan", "kann"] 
relation["kang"] = ["ㄎㄤ", "kang", "karng", "kaang", "kanq"] 
relation["kao"] = ["ㄎㄠ", "kau", "kaur", "kao", "kaw"] 
relation["ke"] = ["ㄎㄜ", "ke", "ker", "kee", "keh"] 
relation["ken"] = ["ㄎㄣ", "ken", "kern", "keen", "kenn"] 
relation["keng"] = ["ㄎㄥ", "keng", "kerng", "keeng", "kenq"] 
relation["kong"] = ["ㄎㄨㄥ", "kong", "korng", "koong", "konq"] 
relation["kou"] = ["ㄎㄡ", "kou", "kour", "koou", "kow"] 
relation["ku"] = ["ㄎㄨ", "ku", "kwu", "kuu", "kuh"] 
relation["kua"] = ["ㄎㄨㄚ", "kua", "kwa", "koa", "kuah"] 
relation["kuai"] = ["ㄎㄨㄞ", "kuai", "kwai", "koai", "kuay"] 
relation["kuan"] = ["ㄎㄨㄢ", "kuan", "kwan", "koan", "kuann"] 
relation["kuang"] = ["ㄎㄨㄤ", "kuang", "kwang", "koang", "kuanq"] 
relation["kui"] = ["ㄎㄨㄟ", "kuei", "kwei", "koei", "kuey"] 
relation["kun"] = ["ㄎㄨㄣ", "kuen", "kwen", "koen", "kuenn"] 
relation["kuo"] = ["ㄎㄨㄛ", "kuo", "kwo", "kuoo", "kuoh"] 
relation["la"] = ["ㄌㄚ", "lha", "la", "laa", "lah"] 
relation["lai"] = ["ㄌㄞ", "lhai", "lai", "lae", "lay"] 
relation["lan"] = ["ㄌㄢ", "lhan", "lan", "laan", "lann"] 
relation["lang"] = ["ㄌㄤ", "lhang", "lang", "laang", "lanq"] 
relation["lao"] = ["ㄌㄠ", "lhau", "lau", "lao", "law"] 
relation["le"] = ["ㄌㄜ", "lhe", "le", "lee", "leh"] 
relation["lei"] = ["ㄌㄟ", "lhei", "lei", "leei", "ley"] 
relation["leng"] = ["ㄌㄥ", "lheng", "leng", "leeng", "lenq"] 
relation["li"] = ["ㄌㄧ", "lhi", "li", "lii", "lih"] 
relation["lia"] = ["ㄌㄧㄚ", "lhia", "lia", "lea", "liah"] 
relation["lian"] = ["ㄌㄧㄢ", "lhian", "lian", "lean", "liann"] 
relation["liang"] = ["ㄌㄧㄤ", "lhiang", "liang", "leang", "lianq"] 
relation["liao"] = ["ㄌㄧㄠ", "lhiau", "liau", "leau", "liaw"] 
relation["lie"] = ["ㄌㄧㄝ", "lhie", "lie", "liee", "lieh"] 
relation["lin"] = ["ㄌㄧㄣ", "lhin", "lin", "liin", "linn"] 
relation["ling"] = ["ㄌㄧㄥ", "lhing", "ling", "liing", "linq"] 
relation["liu"] = ["ㄌㄧㄡ", "lhiou", "liou", "leou", "liow"] 
relation["l"] = ["ㄌㄩ", "ü", "lhiu", "liu", "leu", "liuh"]
relation["l"] = ["ㄌㄩㄝ", "üe", "lhiue", "liue", "leue", "liueh"]
relation["l"] = ["ㄌㄩㄣ", "ün", "lhiun", "liun", "leun", "liunn"]
relation["long"] = ["ㄌㄨㄥ", "lhong", "long", "loong", "lonq"] 
relation["lou"] = ["ㄌㄡ", "lhou", "lou", "loou", "low"] 
relation["lu"] = ["ㄌㄨ", "lhu", "lu", "luu", "luh"] 
relation["luan"] = ["ㄌㄨㄢ", "lhuan", "luan", "loan", "luann"] 
relation["lun"] = ["ㄌㄨㄣ", "lhuen", "luen", "loen", "luenn"] 
relation["luo"] = ["ㄌㄨㄛ", "lhuo", "luo", "luoo", "luoh"] 
relation["lo"] = ["ㄌㄛ", "lo", "lor", "loo", "loh"] 
relation["me"] = ["ㄇㄜ", "me", "mer", "mee", "meh"] 
relation["ma"] = ["ㄇㄚ", "mha", "ma", "maa", "mah"] 
relation["mai"] = ["ㄇㄞ", "mhai", "mai", "mae", "may"] 
relation["man"] = ["ㄇㄢ", "mhan", "man", "maan", "mann"] 
relation["mang"] = ["ㄇㄤ", "mhang", "mang", "maang", "manq"] 
relation["mao"] = ["ㄇㄠ", "mhau", "mau", "mao", "maw"] 
relation["mei"] = ["ㄇㄟ", "mhei", "mei", "meei", "mey"] 
relation["men"] = ["ㄇㄣ", "mhen", "men", "meen", "menn"] 
relation["meng"] = ["ㄇㄥ", "mheng", "meng", "meeng", "menq"] 
relation["mi"] = ["ㄇㄧ", "mhi", "mi", "mii", "mih"] 
relation["mian"] = ["ㄇㄧㄢ", "mhian", "mian", "mean", "miann"] 
relation["miao"] = ["ㄇㄧㄠ", "mhiau", "miau", "meau", "miaw"] 
relation["mie"] = ["ㄇㄧㄝ", "mhie", "mie", "miee", "mieh"] 
relation["min"] = ["ㄇㄧㄣ", "mhin", "min", "miin", "minn"] 
relation["ming"] = ["ㄇㄧㄥ", "mhing", "ming", "miing", "minq"] 
relation["miu"] = ["ㄇㄧㄡ", "mhiou", "miou", "meou", "miow"] 
relation["mo"] = ["ㄇㄛ", "mho", "mo", "moo", "moh"] 
relation["mou"] = ["ㄇㄡ", "mhou", "mou", "moou", "mow"] 
relation["mu"] = ["ㄇㄨ", "mhu", "mu", "muu", "muh"] 
relation["na"] = ["ㄋㄚ", "nha", "na", "naa", "nah"] 
relation["nai"] = ["ㄋㄞ", "nhai", "nai", "nae", "nay"] 
relation["nan"] = ["ㄋㄢ", "nhan", "nan", "naan", "nann"] 
relation["nang"] = ["ㄋㄤ", "nhang", "nang", "naang", "nanq"] 
relation["nao"] = ["ㄋㄠ", "nhau", "nau", "nao", "naw"] 
relation["ne"] = ["ㄋㄜ", "nhe", "ne", "nee", "neh"] 
relation["nei"] = ["ㄋㄟ", "nhei", "nei", "neei", "ney"] 
relation["nen"] = ["ㄋㄣ", "nhen", "nen", "neen", "nenn"] 
relation["neng"] = ["ㄋㄥ", "nheng", "neng", "neeng", "nenq"] 
relation["ni"] = ["ㄋㄧ", "nhi", "ni", "nii", "nih"] 
relation["nian"] = ["ㄋㄧㄢ", "nhian", "nian", "nean", "niann"] 
relation["niang"] = ["ㄋㄧㄤ", "nhiang", "niang", "neang", "nianq"] 
relation["niao"] = ["ㄋㄧㄠ", "nhiau", "niau", "neau", "niaw"] 
relation["nie"] = ["ㄋㄧㄝ", "nhie", "nie", "niee", "nieh"] 
relation["nin"] = ["ㄋㄧㄣ", "nhin", "nin", "niin", "ninn"] 
relation["ning"] = ["ㄋㄧㄥ", "nhing", "ning", "niing", "ninq"] 
relation["niu"] = ["ㄋㄧㄡ", "nhiou", "niou", "neou", "niow"] 
relation["n"] = ["ㄋㄩ", "ü," "nhiu", "niu", "neu", "niuh"]
relation["n"] = ["ㄋㄩㄝ", "üe", "nhiue", "niue", "neue", "niueh"]
relation["nong"] = ["ㄋㄨㄥ", "nhong", "nong", "noong", "nonq"] 
relation["nou"] = ["ㄋㄡ", "nhou", "nou", "noou", "now"] 
relation["nu"] = ["ㄋㄨ", "nhu", "nu", "nuu", "nuh"] 
relation["nuan"] = ["ㄋㄨㄢ", "nhuan", "nuan", "noan", "nuann"] 
relation["nun"] = ["ㄋㄨㄣ", "nhuen", "nuen", "noen", "nuenn"] 
relation["nuo"] = ["ㄋㄨㄛ", "nhuo", "nuo", "nuoo", "nuoh"] 
relation["nia"] = ["ㄋㄧㄚ", "nia", "niar", "niaa", "niah"] 
relation["ou"] = ["ㄡ", "ou", "our", "oou", "ow"] 
relation["pa"] = ["ㄆㄚ", "pa", "par", "paa", "pah"] 
relation["pai"] = ["ㄆㄞ", "pai", "pair", "pae", "pay"] 
relation["pan"] = ["ㄆㄢ", "pan", "parn", "paan", "pann"] 
relation["pang"] = ["ㄆㄤ", "pang", "parng", "paang", "panq"] 
relation["pao"] = ["ㄆㄠ", "pau", "paur", "pao", "paw"] 
relation["pei"] = ["ㄆㄟ", "pei", "peir", "peei", "pey"] 
relation["pen"] = ["ㄆㄣ", "pen", "pern", "peen", "penn"] 
relation["peng"] = ["ㄆㄥ", "peng", "perng", "peeng", "penq"] 
relation["pi"] = ["ㄆㄧ", "pi", "pyi", "pii", "pih"] 
relation["pian"] = ["ㄆㄧㄢ", "pian", "pyan", "pean", "piann"] 
relation["piao"] = ["ㄆㄧㄠ", "piau", "pyau", "peau", "piaw"] 
relation["pie"] = ["ㄆㄧㄝ", "pie", "pye", "piee", "pieh"] 
relation["pin"] = ["ㄆㄧㄣ", "pin", "pyn", "piin", "pinn"] 
relation["ping"] = ["ㄆㄧㄥ", "ping", "pyng", "piing", "pinq"] 
relation["po"] = ["ㄆㄛ", "po", "por", "poo", "poh"] 
relation["pou"] = ["ㄆㄡ", "pou", "pour", "poou", "pow"] 
relation["pu"] = ["ㄆㄨ", "pu", "pwu", "puu", "puh"] 
relation["ran"] = ["ㄖㄢ", "rhan", "ran", "raan", "rann"] 
relation["rang"] = ["ㄖㄤ", "rhang", "rang", "raang", "ranq"] 
relation["rao"] = ["ㄖㄠ", "rhau", "rau", "rao", "raw"] 
relation["re"] = ["ㄖㄜ", "rhe", "re", "ree", "reh"] 
relation["ren"] = ["ㄖㄣ", "rhen", "ren", "reen", "renn"] 
relation["reng"] = ["ㄖㄥ", "rheng", "reng", "reeng", "renq"] 
relation["rong"] = ["ㄖㄨㄥ", "rhong", "rong", "roong", "ronq"] 
relation["rou"] = ["ㄖㄡ", "rhou", "rou", "roou", "row"] 
relation["ru"] = ["ㄖㄨ", "rhu", "ru", "ruu", "ruh"] 
relation["ruan"] = ["ㄖㄨㄢ", "rhuan", "ruan", "roan", "ruann"] 
relation["rui"] = ["ㄖㄨㄟ", "rhuei", "ruei", "roei", "ruey"] 
relation["run"] = ["ㄖㄨㄣ", "rhuen", "ruen", "roen", "ruenn"] 
relation["ruo"] = ["ㄖㄨㄛ", "rhuo", "ruo", "ruoo", "ruoh"] 
relation["ri"] = ["ㄖ", "rhy", "ry", "ryy", "ryh"] 
relation["sa"] = ["ㄙㄚ", "sa", "sar", "saa", "sah"] 
relation["sai"] = ["ㄙㄞ", "sai", "sair", "sae", "say"] 
relation["san"] = ["ㄙㄢ", "san", "sarn", "saan", "sann"] 
relation["sang"] = ["ㄙㄤ", "sang", "sarng", "saang", "sanq"] 
relation["sao"] = ["ㄙㄠ", "sau", "saur", "sao", "saw"] 
relation["se"] = ["ㄙㄜ", "se", "ser", "see", "seh"] 
relation["sei"] = ["ㄙㄟ", "sei", "seir", "seei", "sey"] 
relation["sen"] = ["ㄙㄣ", "sen", "sern", "seen", "senn"] 
relation["seng"] = ["ㄙㄥ", "seng", "serng", "seeng", "senq"] 
relation["sha"] = ["ㄕㄚ", "sha", "shar", "shaa", "shah"] 
relation["shai"] = ["ㄕㄞ", "shai", "shair", "shae", "shay"] 
relation["shan"] = ["ㄕㄢ", "shan", "sharn", "shaan", "shann"] 
relation["shang"] = ["ㄕㄤ", "shang", "sharng", "shaang", "shanq"] 
relation["shao"] = ["ㄕㄠ", "shau", "shaur", "shao", "shaw"] 
relation["she"] = ["ㄕㄜ", "she", "sher", "shee", "sheh"] 
relation["shei"] = ["ㄕㄟ", "shei", "sheir", "sheei", "shey"] 
relation["shen"] = ["ㄕㄣ", "shen", "shern", "sheen", "shenn"] 
relation["sheng"] = ["ㄕㄥ", "sheng", "sherng", "sheeng", "shenq"] 
relation["xi"] = ["ㄒㄧ", "shi", "shyi", "shii", "shih"] 
relation["xia"] = ["ㄒㄧㄚ", "shia", "shya", "shea", "shiah"] 
relation["xian"] = ["ㄒㄧㄢ", "shian", "shyan", "shean", "shiann"] 
relation["xiang"] = ["ㄒㄧㄤ", "shiang", "shyang", "sheang", "shianq"] 
relation["xiao"] = ["ㄒㄧㄠ", "shiau", "shyau", "sheau", "shiaw"] 
relation["xie"] = ["ㄒㄧㄝ", "shie", "shye", "shiee", "shieh"] 
relation["xin"] = ["ㄒㄧㄣ", "shin", "shyn", "shiin", "shinn"] 
relation["xing"] = ["ㄒㄧㄥ", "shing", "shyng", "shiing", "shinq"] 
relation["xiong"] = ["ㄒㄩㄥ", "shiong", "shyong", "sheong", "shionq"] 
relation["xiu"] = ["ㄒㄧㄡ", "shiou", "shyou", "sheou", "shiow"] 
relation["xu"] = ["ㄒㄩ", "shiu", "shyu", "sheu", "shiuh"] 
relation["xuan"] = ["ㄒㄩㄢ", "shiuan", "shyuan", "sheuan", "shiuann"] 
relation["xue"] = ["ㄒㄩㄝ", "shiue", "shyue", "sheue", "shiueh"] 
relation["xun"] = ["ㄒㄩㄣ", "shiun", "shyun", "sheun", "shiunn"] 
relation["shong"] = ["ㄕㄨㄥ", "shong", "shorng", "shoong", "shonq"] 
relation["shou"] = ["ㄕㄡ", "shou", "shour", "shoou", "show"] 
relation["shu"] = ["ㄕㄨ", "shu", "shwu", "shuu", "shuh"] 
relation["shua"] = ["ㄕㄨㄚ", "shua", "shwa", "shoa", "shuah"] 
relation["shuai"] = ["ㄕㄨㄞ", "shuai", "shwai", "shoai", "shuay"] 
relation["shuan"] = ["ㄕㄨㄢ", "shuan", "shwan", "shoan", "shuann"] 
relation["shuang"] = ["ㄕㄨㄤ", "shuang", "shwang", "shoang", "shuanq"] 
relation["shui"] = ["ㄕㄨㄟ", "shuei", "shwei", "shoei", "shuey"] 
relation["shun"] = ["ㄕㄨㄣ", "shuen", "shwen", "shoen", "shuenn"] 
relation["shuo"] = ["ㄕㄨㄛ", "shuo", "shwo", "shuoo", "shuoh"] 
relation["shi"] = ["ㄕ", "shy", "shyr", "shyy", "shyh"] 
relation["song"] = ["ㄙㄨㄥ", "song", "sorng", "soong", "sonq"] 
relation["sou"] = ["ㄙㄡ", "sou", "sour", "soou", "sow"] 
relation["su"] = ["ㄙㄨ", "su", "swu", "suu", "suh"] 
relation["suan"] = ["ㄙㄨㄢ", "suan", "swan", "soan", "suann"] 
relation["sui"] = ["ㄙㄨㄟ", "suei", "swei", "soei", "suey"] 
relation["sun"] = ["ㄙㄨㄣ", "suen", "swen", "soen", "suenn"] 
relation["suo"] = ["ㄙㄨㄛ", "suo", "swo", "suoo", "suoh"] 
relation["si"] = ["ㄙ", "sy", "syr", "syy", "syh"] 
relation["ta"] = ["ㄊㄚ", "ta", "tar", "taa", "tah"] 
relation["tai"] = ["ㄊㄞ", "tai", "tair", "tae", "tay"] 
relation["tan"] = ["ㄊㄢ", "tan", "tarn", "taan", "tann"] 
relation["tang"] = ["ㄊㄤ", "tang", "tarng", "taang", "tanq"] 
relation["tao"] = ["ㄊㄠ", "tau", "taur", "tao", "taw"] 
relation["te"] = ["ㄊㄜ", "te", "ter", "tee", "teh"] 
relation["teng"] = ["ㄊㄥ", "teng", "terng", "teeng", "tenq"] 
relation["ti"] = ["ㄊㄧ", "ti", "tyi", "tii", "tih"] 
relation["tian"] = ["ㄊㄧㄢ", "tian", "tyan", "tean", "tiann"] 
relation["tiao"] = ["ㄊㄧㄠ", "tiau", "tyau", "teau", "tiaw"] 
relation["tie"] = ["ㄊㄧㄝ", "tie", "tye", "tiee", "tieh"] 
relation["ting"] = ["ㄊㄧㄥ", "ting", "tyng", "tiing", "tinq"] 
relation["tong"] = ["ㄊㄨㄥ", "tong", "torng", "toong", "tonq"] 
relation["tou"] = ["ㄊㄡ", "tou", "tour", "toou", "tow"] 
relation["ca"] = ["ㄘㄚ", "tsa", "tsar", "tsaa", "tsah"] 
relation["cai"] = ["ㄘㄞ", "tsai", "tsair", "tsae", "tsay"] 
relation["can"] = ["ㄘㄢ", "tsan", "tsarn", "tsaan", "tsann"] 
relation["cang"] = ["ㄘㄤ", "tsang", "tsarng", "tsaang", "tsanq"] 
relation["cao"] = ["ㄘㄠ", "tsau", "tsaur", "tsao", "tsaw"] 
relation["ce"] = ["ㄘㄜ", "tse", "tser", "tsee", "tseh"] 
relation["cen"] = ["ㄘㄣ", "tsen", "tsern", "tseen", "tsenn"] 
relation["ceng"] = ["ㄘㄥ", "tseng", "tserng", "tseeng", "tsenq"] 
relation["cong"] = ["ㄘㄨㄥ", "tsong", "tsorng", "tsoong", "tsonq"] 
relation["cou"] = ["ㄘㄡ", "tsou", "tsour", "tsoou", "tsow"] 
relation["cu"] = ["ㄘㄨ", "tsu", "tswu", "tsuu", "tsuh"] 
relation["cuan"] = ["ㄘㄨㄢ", "tsuan", "tswan", "tsoan", "tsuann"] 
relation["cui"] = ["ㄘㄨㄟ", "tsuei", "tswei", "tsoei", "tsuey"] 
relation["cun"] = ["ㄘㄨㄣ", "tsuen", "tswen", "tsoen", "tsuenn"] 
relation["cuo"] = ["ㄘㄨㄛ", "tsuo", "tswo", "tsuoo", "tsuoh"] 
relation["ci"] = ["ㄘ", "tsy", "tsyr", "tsyy", "tsyh"] 
relation["tu"] = ["ㄊㄨ", "tu", "twu", "tuu", "tuh"] 
relation["tuan"] = ["ㄊㄨㄢ", "tuan", "twan", "toan", "tuann"] 
relation["tui"] = ["ㄊㄨㄟ", "tuei", "twei", "toei", "tuey"] 
relation["tun"] = ["ㄊㄨㄣ", "tuen", "twen", "toen", "tuenn"] 
relation["tuo"] = ["ㄊㄨㄛ", "tuo", "two", "tuoo", "tuoh"] 
relation["za"] = ["ㄗㄚ", "tza", "tzar", "tzaa", "tzah"] 
relation["zai"] = ["ㄗㄞ", "tzai", "tzair", "tzae", "tzay"] 
relation["zan"] = ["ㄗㄢ", "tzan", "tzarn", "tzaan", "tzann"] 
relation["zang"] = ["ㄗㄤ", "tzang", "tzarng", "tzaang", "tzanq"] 
relation["zao"] = ["ㄗㄠ", "tzau", "tzaur", "tzao", "tzaw"] 
relation["ze"] = ["ㄗㄜ", "tze", "tzer", "tzee", "tzeh"] 
relation["zei"] = ["ㄗㄟ", "tzei", "tzeir", "tzeei", "tzey"] 
relation["zen"] = ["ㄗㄣ", "tzen", "tzern", "tzeen", "tzenn"] 
relation["zeng"] = ["ㄗㄥ", "tzeng", "tzerng", "tzeeng", "tzenq"] 
relation["zong"] = ["ㄗㄨㄥ", "tzong", "tzorng", "tzoong", "tzonq"] 
relation["zou"] = ["ㄗㄡ", "tzou", "tzour", "tzoou", "tzow"] 
relation["zu"] = ["ㄗㄨ", "tzu", "tzwu", "tzuu", "tzuh"] 
relation["zuan"] = ["ㄗㄨㄢ", "tzuan", "tzwan", "tzoan", "tzuann"] 
relation["zui"] = ["ㄗㄨㄟ", "tzuei", "tzwei", "tzoei", "tzuey"] 
relation["zun"] = ["ㄗㄨㄣ", "tzuen", "tzwen", "tzoen", "tzuenn"] 
relation["zuo"] = ["ㄗㄨㄛ", "tzuo", "tzwo", "tzuoo", "tzuoh"] 
relation["zi"] = ["ㄗ", "tzy", "tzyr", "tzyy", "tzyh"] 
relation["wu"] = ["ㄨ", "u", "wu", "wuu", "wuh"] 
relation["wa"] = ["ㄨㄚ", "ua", "wa", "waa", "wah"] 
relation["wai"] = ["ㄨㄞ", "uai", "wai", "woai", "way"] 
relation["wan"] = ["ㄨㄢ", "uan", "wan", "woan", "wann"] 
relation["wang"] = ["ㄨㄤ", "uang", "wang", "woang", "wanq"] 
relation["wei"] = ["ㄨㄟ", "uei", "wei", "woei", "wey"] 
relation["wen"] = ["ㄨㄣ", "uen", "wen", "woen", "wenn"] 
relation["weng"] = ["ㄨㄥ", "ueng", "weng", "woeng", "wenq"] 
relation["wo"] = ["ㄨㄛ", "uo", "wo", "woo", "woh"] 

def list_to_csv(target_path, data):
    if not data:
        raise Exception(f"data for {target_path} corrupted")

    with open(target_path, "w") as outfile:
        writer = csv.writer(outfile)
        for line in data:
            if isinstance(line, list):
                writer.writerow(line)
            else:
                writer.writerow([line])

def csv_to_list(target_path):
    with open(target_path, "r") as infile:
        reader = csv.reader(infile)
        return list(_ if len(_) > 1 else _[0] for _ in reader)

def process_word(word):
    tones = {}
    tones[1]="ĀāĒēĪīŌōŪūÜü"
    tones[2]="ÁáÉéÍíÓóÚúǗǘ"
    tones[3]="ǍǎĚěǏǐǑǒǓǔǙǚ"
    tones[4]="ÀàÈèÌìÒòÙùǛǜ"
    letters = {}
    letters["a"]="ĀāÁáǍǎÀà"
    letters["e"]="ĒēÉéĚěÈè"
    letters["i"]="ĪīÍíǏǐÌì"
    letters["o"]="ŌōÓóǑǒÒò"
    letters["u"]="ŪūÚúǓǔÙùÜüǗǘǙǚǛǜ"

    tone = 1
    for i in tones:
        for let in tones[i]:
            if let in word:
                tone = i
                break

    for letter_group in letters:
        for variant in letters[letter_group]:
            if variant in word:
                word = word.replace(variant, letter_group)
    word = word.lower()

    key = word
    #key = feature[1]
    #tone = 1 if "1" in key else 2 if "2" in key else 3 if "3" in key else 4
    #key = key.lower().replace(str(tone),"")

    if key in relation:
        related = relation[key]
        return  related[tone]
    else:
        print(key)
        return key

def validate_word(word):
    pinyin_letters = ""
    pinyin_letters+="ĀāĒēĪīŌōŪūÜü"
    pinyin_letters+="ÁáÉéÍíÓóÚúǗǘ"
    pinyin_letters+="ǍǎĚěǏǐǑǒǓǔǙǚ"
    pinyin_letters+="ÀàÈèÌìÒòÙùǛǜ"
    for letter in pinyin_letters:
        if letter in word:
            return True
    return False

infile = "/mnt/X/WORKSHOP/Scripts/chained_learning/learning_sets/hsk_rad/features.csv"
features = csv_to_list(infile)
for feature in features:
    for i, test_word in enumerate(feature):
        if not validate_word(test_word):
            continue
        key = feature[i]
        converted = " ".join(process_word(word) for word in key.split(" "))
        feature[i] = converted

list_to_csv(infile, features)
