"""
-*- coding: utf-8 -*-
File: main.py
File Created: Friday, 2nd February 2024
by: Eilles Wan (EillesWan@outlook.com)
Original Author: Wang, Yi (denniswangyi@gmail.com)
"""

from datetime import datetime, timedelta
from itertools import accumulate
from .constants import LUNARNEWYEAR, LUNARYEARCODE, ZHNUMS, SHENGXIAO, TIANGAN, DIZHI


class ZhDate:
    def __init__(self, lunar_year, lunar_month, lunar_day, leap_month=False):
        """初始化函数

        Arguments:
            lunar_year {int} -- 农历年
            lunar_month {int} -- 农历月份
            lunar_day {int} -- 农历日

        Keyword Arguments:
            leap_month {bool} -- 是否是在农历闰月中 (default: {False})
        """
        self.lunar_year = lunar_year
        self.lunar_month = lunar_month
        self.lunar_day = lunar_day
        self.leap_month = leap_month
        self.year_code = LUNARYEARCODE[self.lunar_year - 1900]
        self.newyear = datetime.strptime(LUNARNEWYEAR[self.lunar_year - 1900], "%Y%m%d")
        if not ZhDate.validate(lunar_year, lunar_month, lunar_day, leap_month):
            raise TypeError(
                "农历日期不支持所谓“{}”，超出农历1900年1月1日至2100年12月29日，或日期不存在".format(
                    self
                )
            )

    def to_datetime(self):
        """农历日期转换称公历日期

        Returns:
            datetime -- 当前农历对应的公历日期
        """
        return self.newyear + timedelta(days=self.__days_passed())

    @classmethod
    def from_datetime(cls, dt):
        """类方法，从公历日期生成农历日期

        Arguments:
            dt {datetime} -- 公历的日期

        Returns:
            ZhDate -- 生成的农历日期对象
        """
        lunar_year = dt.year
        # 如果还没有到农历正月初一 农历年份减去1
        lunar_year -= (
            datetime.strptime(LUNARNEWYEAR[lunar_year - 1900], "%Y%m%d") - dt
        ).total_seconds() > 0
        # 当时农历新年时的日期对象
        newyear_dt = datetime.strptime(LUNARNEWYEAR[lunar_year - 1900], "%Y%m%d")
        # 查询日期距离当年的春节差了多久
        days_passed = (dt - newyear_dt).days
        # 被查询日期的年份码
        year_code = LUNARYEARCODE[lunar_year - 1900]
        # 取得本年的月份列表
        month_days = cls.decode(year_code)

        for pos, days in enumerate(accumulate(month_days)):
            if days_passed + 1 <= days:
                month = pos + 1
                lunar_day = month_days[pos] - (days - days_passed) + 1
                break

        leap_month = False
        if (year_code & 0xF) == 0 or month <= (year_code & 0xF):
            lunar_month = month
        else:
            lunar_month = month - 1

        if (year_code & 0xF) != 0 and month == (year_code & 0xF) + 1:
            leap_month = True

        return cls(lunar_year, lunar_month, lunar_day, leap_month)

    @classmethod
    def today(cls):
        """类方法，返回今日的农历日期

        Returns:
            ZhDate -- 生成的今日农历日期对象
        """
        return cls.from_datetime(datetime.now())

    def __days_passed(self):
        """私有方法，计算当前农历日期和当年农历新年之间的天数差值

        Returns:
            int -- 差值天数
        """
        month_days = ZhDate.decode(self.year_code)
        # 当前农历年的闰月，为0表示无润叶
        month_leap = self.year_code & 0xF

        # 当年无闰月，或者有闰月但是当前月小于闰月
        if (month_leap == 0) or (self.lunar_month < month_leap):
            days_passed_month = sum(month_days[: self.lunar_month - 1])
        # 当前不是闰月，并且当前月份和闰月相同
        elif (not self.leap_month) and (self.lunar_month == month_leap):
            days_passed_month = sum(month_days[: self.lunar_month - 1])
        else:
            days_passed_month = sum(month_days[: self.lunar_month])

        return days_passed_month + self.lunar_day - 1

    def chinese(self):
        zh_year = ""
        for i in range(0, 4):
            zh_year += ZHNUMS[int(str(self.lunar_year)[i])]

        if self.leap_month:
            zh_month = "闰"
        else:
            zh_month = ""

        if self.lunar_month == 1:
            zh_month += "正"
        elif self.lunar_month == 12:
            zh_month += "腊"
        elif self.lunar_month <= 10:
            zh_month += ZHNUMS[self.lunar_month]
        else:
            zh_month += "十{}".format(ZHNUMS[self.lunar_month - 10])

        if self.lunar_day <= 10:
            zh_day = "初{}".format(ZHNUMS[self.lunar_day])
        elif self.lunar_day < 20:
            zh_day = "十{}".format(ZHNUMS[self.lunar_day - 10])
        elif self.lunar_day == 20:
            zh_day = "二十"
        elif self.lunar_day < 30:
            zh_day = "廿{}".format(ZHNUMS[self.lunar_day - 20])
        else:
            zh_day = "三十"

        year_tiandi = ZhDate.__tiandi(self.lunar_year - 1900 + 36)

        return "{}年{}月{} {}{}年".format(
            zh_year,
            zh_month,
            zh_day,
            year_tiandi,
            SHENGXIAO[(self.lunar_year - 1900) % 12],
        )

    def __str__(self):
        """打印字符串的方法

        Returns:
            str -- 标准格式农历日期字符串
        """
        return "农历{}年{}{}月{}日".format(
            self.lunar_year,
            "闰" if self.leap_month else "",
            self.lunar_month,
            self.lunar_day,
        )

    def __format__(self, __format_spec: str) -> str:
        """格式化打印字符串的方法

        Returns:
            str -- 指定格式的农历日期字符串
        """
        # 我在这里思考了一下，要不要再加一个参数用来指定年月日的输出顺序
        # 然后突然想到，哦，我在做的是农历的日期库
        # 农历的日期库调什么年月日的顺序，天下农历是一家啊！
        # 咱华夏文明才是独出农历啊！更何况，算上汉语文化圈，也都是这个顺序
        # 没得改没得改，就是这个顺序，要什么年月日的输出顺序嘛
        return self.__str__().__format__(__format_spec)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, another):
        if not isinstance(another, ZhDate):
            raise TypeError("比较必须都是ZhDate类型")
        cond1 = self.lunar_year == another.lunar_year
        cond2 = self.lunar_month == another.lunar_month
        cond3 = self.lunar_day == another.lunar_day
        cond4 = self.leap_month == another.leap_month
        return cond1 and cond2 and cond3 and cond4

    def __add__(self, another):
        if not isinstance(another, int):
            raise TypeError("加法只支持整数天数相加")
        return ZhDate.from_datetime(self.to_datetime() + timedelta(days=another))

    def __sub__(self, another):
        if isinstance(another, int):
            return ZhDate.from_datetime(self.to_datetime() - timedelta(days=another))
        elif isinstance(another, ZhDate):
            return (self.to_datetime() - another.to_datetime()).days
        elif isinstance(another, datetime):
            return (self.to_datetime() - another).days
        else:
            raise TypeError("减法只支持整数，ZhDate, Datetime类型")

    """
    以下为帮助函数
    """

    @staticmethod
    def __tiandi(anum):
        return "{}{}".format(TIANGAN[anum % 10], DIZHI[anum % 12])

    @staticmethod
    def validate(year, month, day, leap):
        """农历日期校验

        Arguments:
            year {int} -- 农历年份
            month {int} -- 农历月份
            day {int} -- 农历日期
            leap {bool} -- 农历是否为闰月日期

        Returns:
            bool -- 校验是否通过
        """
        # 年份低于1900，大于2100，或者月份不属于 1-12，或者日期不属于 1-30，返回校验失败
        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 30):
            return False

        year_code = LUNARYEARCODE[year - 1900]

        # 有闰月标志
        if leap:
            if (year_code & 0xF) != month:  # 年度闰月和校验闰月不一致的话，返回校验失败
                return False
            elif (
                day == 30
            ):  # 如果日期是30的话，直接返回年度代码首位是否为1，即闰月是否为大月
                return (year_code >> 16) == 1
            else:  # 年度闰月和当前月份相同，日期不为30的情况，返回通过
                return True
        elif day <= 29:  # 非闰月，并且日期小于等于29，返回通过
            return True
        else:  # 非闰月日期为30，返回年度代码中的月份位是否为1，即是否为大月
            return ((year_code >> (12 - month) + 4) & 1) == 1

    @staticmethod
    def decode(year_code):
        """解析年度农历代码函数

        Arguments:
            year_code {int} -- 从年度代码数组中获取的代码整数

        Returns:
            list[int, ] -- 当前年度代码解析以后形成的每月天数数组，已将闰月嵌入对应位置，即有闰月的年份返回的列表长度为13，否则为12
        """
        # 请问您为什么不在这么重要的地方写注释？
        month_days = []
        for i in range(4, 16):
            # 向右移动相应的位数
            # 1 这个数只有一位，与任何数进行 按位与 都只能获得其
            # 从后往前第一位，对！是获得这一位
            month_days.insert(0, 30 if (year_code >> i) & 1 else 29)

        # 0xf 即 15 即二进制的 1111
        # 所以 1111 与任何数进行 按位与
        # 都将获得其最后四位，对！是获得这最后四位
        # 后四位非0则表示有闰月（多一月），则插入一次月份
        # 而首四位表示闰月的天数
        if year_code & 0xF:
            month_days.insert((year_code & 0xF), 30 if year_code >> 16 else 29)

        # 返回一个列表
        return month_days

    @staticmethod
    def month_days(year):
        """根据年份返回当前农历月份天数list

        Arguments:
            year {int} -- 1900到2100的之间的整数

        Returns:
            [int] -- 农历年份所对应的农历月份天数列表
        """
        return ZhDate.decode(LUNARYEARCODE[year - 1900])
