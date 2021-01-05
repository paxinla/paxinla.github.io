Title: [转] 纸牌加密
Date: 2020-12-30 12:04:22
Category: 密码学
Tags: 转载, card
CommentId: X

原文作者: Golden Grape

原文链接: [https://goldengrape.github.io/posts/bulabula/Solitaire_Encryption/](https://goldengrape.github.io/posts/bulabula/Solitaire_Encryption/)

为防遗失，转载一份。

<!-- PELICAN_END_SUMMARY -->

## 纸牌加密

这是记录在[《编码宝典》](https://book.douban.com/subject/27077159/)附录里的一个手工加密方法.

所谓手工加密，就是完全不依赖于计算机，靠一副纸牌就可以产生连续的加密用密钥。纸牌的顺序就是密码，所以密码的可能数量=54的阶乘，大致是2.31后面跟上71个0。

军用级。

很可惜，这个加密方法并不是RSA那样的公私钥加密系统。所以，密码必须事先传递好。加密/解密的双方，必须知道同一副纸牌的顺序。可以是双方把牌的顺序背下来，也可以是双方各自持有一副同样顺序的纸牌。我觉得背下来更保险，貌似也是可以做到的。

<p class="list-title">产生连续密钥的方法是这样的：</p>

1. 拿出纸牌，面向上。下面的讲解中，我以一副新的纸牌为例，起始纸牌的顺序如下，这也是牌面的数值，从 1-52, 53, 54 : ♣A，♣2...♣K，<span style="color: red !important;">♦</span>A...<span style="color: red !important;">♦</span>K，<span style="color: red !important;">♥</span>A...<span style="color: red !important;">♥</span>K，♠A...♠K，小王，大王。
2. 找到小王，向下移动一张，如果小王已经是最后一张牌，则挪到第一张。♣A，♣2...♣K，<span style="color: red !important;">♦</span>A...<span style="color: red !important;">♦</span>K，<span style="color: red !important;">♥</span>A...<span style="color: red !important;">♥</span>K，♠A...♠K，大王，小王。
3. 找到大王，向下移动两张。♣A，大王，♣2...♣K，<span style="color: red !important;">♦</span>A...<span style="color: red !important;">♦</span>K，<span style="color: red !important;">♥</span>A...<span style="color: red !important;">♥</span>K，♠A...♠K，小王。
4. 做一次三切牌。将两个王和其之间的牌作为B组，从第一张到上面的王前一张是A组，从下面的王后一张到最后一张牌是C组。交换A组和C组的牌，从 A-B-C ，变换成 C-B-A 。大王，♣2...♣K，<span style="color: red !important;">♦</span>A...<span style="color: red !important;">♦</span>K，<span style="color: red !important;">♥</span>A...<span style="color: red !important;">♥</span>K，♠A...♠K，小王，♣A 。
5. 找到最后一张牌，看其数字N（大小王都按照53来计数），从第一张开始数N张牌，作为A组，第N+1张牌到倒数第2张牌为B组，交换A组和B组，♣2...♣K，<span style="color: red !important;">♦</span>A...<span style="color: red !important;">♦</span>K，<span style="color: red !important;">♥</span>A...<span style="color: red !important;">♥</span>K，♠A...♠K，小王，大王，♣A 。
6. 看第一张牌的数字N，数N张牌，找到第N+1张牌，就是一个输出的密钥了。这个例子中是 ♣4 。♣2，♣3，<span style="color: green !important;">【</span>♣4<span style="color: green !important;">】</span>...♣K，<span style="color: red !important;">♦</span>A...<span style="color: red !important;">♦</span>K，<span style="color: red !important;">♥</span>A...<span style="color: red !important;">♥</span>K，♠A...♠K，小王，大王，♣A 。
7. 重复上面步骤1-5，连续产生新的密钥。

对于每一个密钥，用法就是简单的移位密码，比如♣4的数值就是4，如果比26大，那么就除以26求余数，比如 `30 mod 26=4` 。那么如果要加密字母A，就是从A+4，数B，C，D，E，得到字母E。

如果是解密，则只是做减法，比如得到的密文是E，减去4，得到原文A。

操作要练习几次，自己容易乱，特别是数数的时候。

按照作者的说明，如果从一副新牌开始，则连续输出的密钥是：

```
4 49 10 (53) 24 8 51 44 6 4 33
```

其中遇到大王小王则跳过.

如果对 `AAAAA AAAAA` 加密，得到的密文结果应当是 `EXKYI ZSGEH` 。

注意:

+ 不可以用同一个密码去加密两个不同的信息!
+ 不可以用同一个密码去加密两个不同的信息!
+ 不可以用同一个密码去加密两个不同的信息!

因为将两个密文相减，密钥的作用就消除了，然后大概可以通过统计学的方式进行解密。

我这段时间正在学习 C++ ，所以也用 C++ 实现了一遍纸牌加密的算法。代码在 [https://github。com/goldengrape/SolitaireEncryption](https://github。com/goldengrape/SolitaireEncryption) 还在调试中，暂时和作者的结果有一点点区别（应该得到51的那个数，我得到了54，前后都一样，很诡异）。

参考资料:

+ [https://www.schneier.com/academic/solitaire/](https://www.schneier.com/academic/solitaire/)

