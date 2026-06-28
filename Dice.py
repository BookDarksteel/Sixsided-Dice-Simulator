# Sixsided Dice Simulator
# Dice.py

from copy import deepcopy
from os import path, rename
from random import choices
from shutil import copy

from constants import *


class Dice(object):
    def __init__(self, dice_name):
        self._name = dice_name
        self._description = ""
        self._folder_path = DICE_FOLDER_PATH + "/" + dice_name
        self._exists = True
        self._inexists_reason = ""
        self._pattern_info = {}
        if self._name == "":
            self._exists = False
            self._inexists_reason = "六面骰名称为空。"
        else:
            try:
                with open(
                    self._folder_path + "/dice_info.txt", "r", encoding="utf-8"
                ) as f:
                    f.readline()
                    f.readline()
                    f.readline()
                    f.readline()
                    f.readline()
                    dice_name_in_info_file = f.readline()[:-1]
                    if dice_name_in_info_file != self._name:
                        self._inexists_reason = (
                            "六面骰名称与记载在六面骰信息文件中的六面骰名称不符。"
                        )
                        raise ValueError(
                            "六面骰名称与记载在六面骰信息文件中的六面骰名称不符。"
                        )
                    f.readline()
                    self._description = f.readline()[:-1]
                    for i in range(1, 7):
                        f.readline()
                        dice_pattern_name = f.readline()[:-1]
                        dice_pattern_pic_file_name = f.readline()[:-1]
                        if not path.exists(
                            self._folder_path + "/" + dice_pattern_pic_file_name
                        ):
                            self._inexists_reason = (
                                "未找到六面骰的" + dice_pattern_name + "面的图片文件。"
                            )
                            raise ValueError(
                                "未找到六面骰的 "
                                + dice_pattern_name
                                + " 面的图片文件。"
                            )
                        dice_pattern_probability_str = f.readline()[:-1]
                        dice_pattern_probability = eval(dice_pattern_probability_str)
                        self._pattern_info[i] = [
                            dice_pattern_name,
                            dice_pattern_pic_file_name,
                            dice_pattern_probability,
                            dice_pattern_probability_str,
                        ]
                    self.throw()
            except Exception:
                self._exists = False
                if self._inexists_reason == "":
                    self._inexists_reason = (
                        "无法正常读取六面骰信息文件，或六面骰信息文件内容不符合规范。"
                    )

    def get_current_pattern_name(self):
        """
        获取本获取本六面骰当前面名称
        返回值：本六面骰当前面名称。
        """
        return self._pattern_info[self._current_pattern_id][0]

    def get_currnet_pattern_pic_file_path(self):
        """
        获取本六面骰当前面图片路径
        返回值：本六面骰当前图案图片从六面骰模拟器工作文件夹开始的相对路径。
        """
        return self._folder_path + "/" + self._pattern_info[self._current_pattern_id][1]

    def get_description(self):
        """
        获取本六面骰的描述信息
        返回值：本六面骰的描述信息。
        """
        return self._description

    def get_exists(self):
        """
        获取本六面骰是否存在
        骰子存在意味着本对象保存有供六面骰模拟器进行模拟的六面骰信息，反之则意味着本对象保存的六面骰信息不能够供六面骰模拟器进行模拟。
        返回值：若骰子存在则返回True，反之则返回False。
        """
        return self._exists

    def get_folder_path(self):
        """
        获取本六面骰的文件夹路径
        返回值：描述本六面骰的文件夹路径的字符串
        """
        return self._folder_path

    def get_inexists_reason(self):
        """
        获取本六面骰不存在的原因
        返回值：本六面骰不存在的原因。若本六面骰存在，则应为空字符串。
        """
        return self._inexists_reason

    def get_name(self):
        """
        获取本六面骰的名称
        返回值：本六面骰的名称。
        """
        return self._name

    def get_pattern_info(self):
        """
        获取本六面骰的骰面信息
        返回值：一个描述本六面骰的骰面信息的字典，该字典的每一项是描述一个骰面的信息的列表。
        """
        return deepcopy(self._pattern_info)

    def modify_pattern_pic(self, pattern_id, new_pic_path):
        """
        修改骰面图片
        将给定图片文件路径的图片复制到根据六面骰骰面信息中给定编号骰面的信息可以定位到的路径，将会覆盖给定编号骰面的旧骰面图片文件。
        参数pattern_id：给定骰面编号。
        参数new_pic_path：给定的新骰面图片文件路径。
        无返回值。
        """
        copy(new_pic_path, self._folder_path + "/" + self._pattern_info[pattern_id][1])

    def throw(self):
        """
        掷骰子
        按照骰子信息选取骰子的骰子面，新选取的骰子面的编号会被更新至self._current_pattern_id。
        无返回值。
        """
        dice_pattern_ids = list(range(1, 7))
        dice_pattern_probabilitis = []
        for dpid in dice_pattern_ids:
            dice_pattern_probabilitis.append(self._pattern_info[dpid][2])
        self._current_pattern_id = choices(dice_pattern_ids, dice_pattern_probabilitis)[
            0
        ]

    def set_description(self, new_description):
        """
        修改本六面骰的描述信息
        参数new_description：新的六面骰描述信息，应为字符串类型。
        无返回值。
        """
        self._description = new_description

    def set_name(self, new_name):
        """
        修改本六面骰的名称
        本函数会一并修改本六面骰文件夹的名称。
        参数new_name：新的六面骰名称，应为字符串类型。
        无返回值。
        """
        if self._name != new_name:
            self._name = new_name
            new_folder_path = DICE_FOLDER_PATH + "/" + self._name
            rename(self._folder_path, new_folder_path)
            self._folder_path = new_folder_path

    def set_pattern_info(self, new_pattern_info):
        """
        修改本六面骰的骰面信息
        参数new_pattern_info：新的保存六面骰骰面信息的字典。
        无返回值。
        """
        self._pattern_info = deepcopy(new_pattern_info)

    def write_dice_info_txt(self):
        """
        写入六面骰信息文件
        将当前的本六面骰信息写入对应的六面骰信息文件，将会覆盖旧的六面骰信息文件。
        无返回值。
        """
        with open(self._folder_path + "/dice_info.txt", "w", encoding="utf-8") as f:
            f.write(DICE_INFO_FILE_HEAD)
            f.write("\n\n")
            f.write(self._name)
            f.write("\n\n")
            f.write(self._description)
            f.write("\n\n")
            for i in range(1, 7):
                f.write(self._pattern_info[i][0])
                f.write("\n")
                f.write(self._pattern_info[i][1])
                f.write("\n")
                f.write(self._pattern_info[i][3])
                f.write("\n\n")

