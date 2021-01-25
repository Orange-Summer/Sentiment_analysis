# -*- coding:utf8 -*-
#大明王
from pyltp import Segmentor
from pyltp import SentenceSplitter
from pyltp import Postagger

#读取文件，文件读取函数
def read_file(filename):
    with  open(filename, 'r',encoding='utf-8')as f:
        text = f.read()
        #返回list类型数据
        text = text.split('\n')
    return text

#文本分句
def cut_sentence(text):
    sentences = SentenceSplitter.split(text)
    sentence_list = [ w for w in sentences]
    return sentence_list

#文本分词
def tokenize(sentence):
    #加载模型
    segmentor = Segmentor()  # 初始化实例
    # 加载模型
    segmentor.load(r'E:\tool\python\Lib\site-packages\pyltp-0.2.1.dist-info\ltp_data\cws.model')
    # 产生分词，segment分词函数
    words = segmentor.segment(sentence)
    words = list(words)
    # 释放模型
    segmentor.release()
    return words

#词性标注
def postagger(words):
    # 初始化实例
    postagger = Postagger()
    # 加载模型
    postagger.load(r'E:\tool\python\Lib\site-packages\pyltp-0.2.1.dist-info\ltp_data\pos.model')
    # 词性标注
    postags = postagger.postag(words)
    # 释放模型
    postagger.release()
    #返回list
    postags = [i for i in postags]
    return postags

# 分词，词性标注，词和词性构成一个元组
def intergrad_word(words,postags):
    #拉链算法，两两匹配
    pos_list = zip(words,postags)
    pos_list = [ w for w in pos_list]
    return pos_list

#去停用词函数
def del_stopwords(words):
    # 读取停用词表
    stopwords = read_file(r"stop_words\stopwords.txt")
    # 去除停用词后的句子
    new_words = []
    for word in words:
        if word not in stopwords:
            new_words.append(word)
    return new_words

# 获取六种权值的词，根据要求返回list，这个函数是为了配合Django的views下的函数使用
def weighted_value(request):
    result_dict = []
    if request == "one":
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\degree_dict\most.txt")
    elif request == "two":
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\degree_dict\very.txt")
    elif request == "three":
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\degree_dict\more.txt")
    elif request == "four":
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\degree_dict\ish.txt")
    elif request == "five":
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\degree_dict\insufficiently.txt")
    elif request == "six":
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\degree_dict\inverse.txt")
    elif request == 'posdict':
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\emotion_dict\pos_all_dict.txt")
    elif request == 'negdict':
        result_dict = read_file(r"E:\学习笔记\NLP学习\NLP code\情感分析3\emotion_dict\neg_all_dict.txt")
    else:
        pass
    return result_dict

print("reading sentiment dict .......")
# 读取情感词典
posdict = weighted_value('posdict')
negdict = weighted_value('negdict')
# 读取程度副词词典
mostdict = weighted_value('one')# 权值为4
verydict = weighted_value('two')# 权值为3
moredict = weighted_value('three')# 权值为2
ishdict = weighted_value('four')# 权值为0.5
insufficientdict = weighted_value('five') # 权值为0.25
inversedict = weighted_value('six')# 权值为-1

#程度副词处理，对不同的程度副词给予不同的权重
def match_adverb(word,sentiment_value):

    #最高级权重为
    if word in mostdict:
        sentiment_value *= 4
    #比较级权重
    elif word in verydict:
        sentiment_value *= 3
    #比较级权重
    elif word in moredict:
        sentiment_value *= 2
    #轻微程度词权重
    elif word in ishdict:
        sentiment_value *= 0.5
    #相对程度词权重
    elif word in insufficientdict:
        sentiment_value *= 0.25
    #否定词权重
    elif word in inversedict:
        sentiment_value *= -1
    else:
        sentiment_value *= 1
    return sentiment_value

#对每一条微博打分
def single_sentiment_score(text_sent):
    sentiment_scores = []
    #对单条微博分句
    sentences = cut_sentence(text_sent)
    for sent in sentences:
        #查看分句结果
        # print('分句：',sent)
        #分词
        words = tokenize(sent)
        seg_words = del_stopwords(words)
        #i，s 记录情感词和程度词出现的位置
        i = 0   #记录扫描到的词位子
        s = 0   #记录情感词的位置
        poscount = 0 #记录积极情感词数目
        negcount = 0 #记录消极情感词数目
        #逐个查找情感词
        for word in seg_words:
            #如果为积极词
            if word in posdict:
                poscount += 1  #情感词数目加1
            #在情感词前面寻找程度副词
                for w in seg_words[s:i]:
                    poscount = match_adverb(w,poscount)
                s = i+1 #记录情感词位置
            # 如果是消极情感词
            elif word in negdict:
                negcount +=1
                for w in seg_words[s:i]:
                    negcount = match_adverb(w,negcount)
                s = i+1
            #如果结尾为感叹号或者问号，表示句子结束，并且倒序查找感叹号前的情感词，权重+4
            elif word =='!' or  word =='！' or word =='?' or word == '？':
                for w2 in seg_words[::-1]:
                    #如果为积极词，poscount+2
                    if w2 in posdict:
                        poscount += 4
                        break
                    #如果是消极词，negcount+2
                    elif w2 in negdict:
                        negcount += 4
                        break
            i += 1 #定位情感词的位置
        #计算情感值
        sentiment_score = poscount - negcount
        sentiment_scores.append(sentiment_score)
        #查看每一句的情感值
        # print('分句分值：',sentiment_score)
    sentiment_sum = 0
    for s in sentiment_scores:
        #计算出一条微博的总得分
        sentiment_sum +=s
    return sentiment_sum

# 分析test_data.txt 中的所有微博，返回一个列表，列表中元素为（分值，微博）元组
def run_score(contents):
    # 待处理数据
    scores_list = []
    for content in contents:
        if content !='':
            score = single_sentiment_score(content)  # 对每条微博调用函数求得打分
            scores_list.append(score) # 形成（分数，微博）元组
    return scores_list

#情感分析函数。调用该函数实现情感分析
def run_analysis(contents):
    print('Processing........')
    scores = run_score(contents)
    sentiment = []
    for score in scores:
        # print('情感分值：',score[0])
        if score > 0:
            # print('情感倾向：积极')
            s = 'pos'
        elif score  == 0:
            # print('情感倾向：中性')
            s = '中性'
        else:
            #print('情感倾向：消极')
            s = 'neg'
        sentiment.append(s)
    print('Analysis Success.........')
    return scores,sentiment

