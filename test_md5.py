import hashlib

def get_token():
    md5str = "https://blog.csdn.net/m0_38080253/article/details/78838489"
    # 生成一个md5对象
    m1 = hashlib.md5()
    # 使用md5对象里的update方法md5转换
    m1.update(md5str.encode("utf-8"))
    token = m1.hexdigest()
    return token

print(get_token())