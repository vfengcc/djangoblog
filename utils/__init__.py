# 读取model指定字段
def jsonify(instance, allow=None, exclude=[]):
    # 先过滤fields 再for循环
    if allow is not None:
        fn = lambda x: x.name in allow
    else:
        fn = lambda x: x.name not in exclude
    return {f.name: getattr(instance, f.name) for f in filter(fn, type(instance)._meta.fields)}
