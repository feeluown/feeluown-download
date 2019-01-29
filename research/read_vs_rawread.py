import time


def test_write_vs_rawwrite(chunk=16, size=1024*1024*16):
    """比较 Python 封装的 f.write 方法和原生的 write 系统调用。

    下面是 chunk=16, 256, 2048, 3072, 4096, 8192 时，Python
    的 write 方法和原生 write 方法对比结果（测试机上的 block size 为 4096）。

    .. code::

        ------------------------
        test_write_vs_rawwrite: chunk=16
        raw_write: 1.8491606712341309
        write: 0.23274922370910645

        ------------------------
        test_write_vs_rawwrite: chunk=256
        raw_write: 0.13067007064819336
        write: 0.030336856842041016

        ------------------------
        test_write_vs_rawwrite: chunk=2048
        raw_write: 0.02978801727294922
        write: 0.01960277557373047

        ------------------------
        test_write_vs_rawwrite: chunk=3072
        raw_write: 0.02814459800720215
        write: 0.025383710861206055

        ------------------------
        test_write_vs_rawwrite: chunk=4096
        raw_write: 0.020773887634277344
        write: 0.021095752716064453

        ------------------------
        test_write_vs_rawwrite: chunk=8192
        raw_write: 0.015554428100585938
        write: 0.016388416290283203

        ------------------------
        test_write_vs_rawwrite: chunk=65536
        raw_write: 0.015977144241333008
        write: 0.013889312744140625

        ------------------------
        test_write_vs_rawwrite: chunk=1048576
        raw_write: 0.01435232162475586
        write: 0.019297122955322266

    Python write 方法是使用了 Buffer 的，也就是攒到一定的内容，
    再真正的调用原生 write 方法。这种方案在需要多次写入小块内容时，
    确实很有效果。但是如果每次写入就是比较大的块，它们则相差无几，
    甚至调用原生 write 方法会更高效一点。
    """
    print('------------------------')
    print('test_write_vs_rawwrite: chunk=%d' % chunk)

    t1 = time.time()
    with open('/tmp/tmp1', 'wb') as f:
        for i in range(0, size // chunk):
            f.raw.write(b'b' * chunk)

    t2 = time.time()
    with open('/tmp/tmp2', 'wb') as f:
        for i in range(0, size // chunk):
            f.write(b'b' * chunk)

    t3 = time.time()

    print('raw_write:', t2 - t1)
    print('write:', t3 - t2)
    print()


if __name__ == '__main__':
    # for i in range(0, 10, 2):
    #     test_write_vs_rawwrite(1 * 2**i)
    #
    # for i in range(10, 20, 2):
    #     test_write_vs_rawwrite(1 * 2**i, size=1024*1024*10)
    test_write_vs_rawwrite(16)
    test_write_vs_rawwrite(256)
    test_write_vs_rawwrite(2048)
    test_write_vs_rawwrite(1024*3)
    test_write_vs_rawwrite(4096)
    test_write_vs_rawwrite(4096 * 2)
    test_write_vs_rawwrite(4096 * 16)
    test_write_vs_rawwrite(4096 * 256)
