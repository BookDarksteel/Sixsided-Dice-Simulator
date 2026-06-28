# Sixsided Dice Simulator
# mian.py

import atexit
import os
import shutil
import sys
import tkinter
import tkinter.ttk

from copy import deepcopy

from constants import *
from Dice import *


build_file_lock = False


@atexit.register
def exit_sixsided_sice_simulator():
    if build_file_lock:
        os.remove(PROGRAM_SINGLE_INSTANCE_LOCK_FILE_PATH)


def add_dice_to_bag(new_dice_path):
    """
    向六面骰包中添加新的六面骰
    此函数会将新六面骰的文件复制到Sixsided Dice Simulator工作区的六面骰文件夹（路径由DICE_FOLDER_PATH的数确定）。
    参数new_dice_path：新的六面骰的文件的路径。
    返回值：一个包含两项的元组，其中第一个值为True或False,表示新六面骰是否成功被添加到六面骰包中；第二个值是一个存有添加成功或失败的描述信息的字符串。
    """
    new_dice_name = os.path.basename(new_dice_path)
    shutil.copytree(new_dice_path, DICE_FOLDER_PATH + "/" + new_dice_name)
    new_dice = Dice(new_dice_name)
    if new_dice.get_exists():
        dice_bag[new_dice_name] = new_dice
        return (True, "添加新的六面骰成功")
    else:
        return (False, new_dice.get_inexists_reason())

def button_about_operation():

    global first_level_sub_window_opened

    def exit_about():
        """
        关闭设置窗口
        无返回值。
        """
        global first_level_sub_window_opened
        first_level_sub_window_opened = False
        window_about.destroy()

    if not first_level_sub_window_opened:
        first_level_sub_window_opened = True

        window_about = tkinter.Toplevel(window_main)
        window_about.title("关于")
        window_about.iconbitmap(PROGRAM_ICON_PATH)
        window_about.resizable(False, False)
        window_about.protocol("WM_DELETE_WINDOW", exit_about)

        label_program_icon_pic = tkinter.Label(
            window_about, image=program_icon_image, justify="left"
        )
        label_program_icon_pic.grid(row=0, column=0, sticky="w")

        label_program_name = tkinter.Label(
            window_about, text=PROGRAM_NAME, justify="left", font=FONT_IMPORTANT
        )
        label_program_name.grid(row=1, column=0, sticky="w")

        label_program_description = tkinter.Label(
            window_about,
            text=PROGRAM_DESCRIPTION,
            justify="left",
            wraplength=500,
            font=FONT_NORMAL,
        )
        label_program_description.grid(row=2, column=0, sticky="w")

        label_program_version = tkinter.Label(
            window_about,
            text="版本：" + VERSION_STR,
            justify="left",
            wraplength=500,
            font=FONT_NORMAL,
        )
        label_program_version.grid(row=3, column=0, sticky="w")

        label_program_development_completion_date = tkinter.Label(
            window_about,
            text="开发完成日期：" + VERSION_COMPLETION_DATE_STR,
            justify="left",
            wraplength=500,
            font=FONT_NORMAL,
        )
        label_program_development_completion_date.grid(row=4, column=0, sticky="w")

        label_program_developer = tkinter.Label(
            window_about,
            text="开发者：" + DEVELOPER,
            justify="left",
            wraplength=500,
            font=FONT_NORMAL,
        )
        label_program_developer.grid(row=5, column=0, sticky="w")

        button_ok = tkinter.Button(
            window_about, text="确定", font=FONT_NORMAL, command=exit_about
        )
        button_ok.grid(row=6, column=0)

def button_edit_dice_info_operation():

    global first_level_sub_window_opened

    def confirm_dice_info():
        """
        确定六面骰信息
        点击button_save后会执行此函数。
        如果有未保存的六面骰信息，则会先保存未保存的六面骰信息，之后关闭编辑六面骰信息窗口；如果没有未保存的六面骰信息，则直接关闭编辑六面骰信息窗口。
        无返回值。
        """
        if (
            new_dice_name_unsaved_mark
            or new_dice_description_unsaved_mark
            or new_dice_pattern_info_unsaved_mark
        ):
            save_dice_info()
        exit_edit_dice_info()

    def double_click_pic_edit(event):
        """
        鼠标左键双击图片以编辑
        双击显示六面骰图像的label_dice_pattern_pic会执行此函数。
        参数event：鼠标左键双击label_dice_pattern_pic的事件。
        无返回值。
        """
        row = treeview_dice_pattern_info.identify_row(
            event.widget.winfo_y() + 1
        )  # “+1”是为了从label_dice_pattern_pic的原点坐标偏移1个像素以确保定位到对应的treeview_dice_pattern_info中的行，否则可能定位到对应的行的上一行。
        edit_dice_pattern_pic(int(row))

    def double_click_treeview_edit(event):
        """
        鼠标左键双击列表以编辑
        双击展示六面骰骰面信息的treeview_dice_pattern_info会执行此函数。
        参数event：鼠标左键双击treeview_dice_pattern_info的事件。
        无返回值。
        """
        nonlocal entry_edit
        row = treeview_dice_pattern_info.identify_row(event.y)
        col = treeview_dice_pattern_info.identify_column(event.x)
        if row:
            if col == "#1" or col == "#3":
                val = treeview_dice_pattern_info.set(row, col)
                x, y, w, h = treeview_dice_pattern_info.bbox(row, col)
                entry_edit = tkinter.Entry(treeview_dice_pattern_info, font=FONT_NORMAL)
                entry_edit.place(x=x, y=y, width=w, height=h)
                entry_edit.insert(0, val)
                entry_edit.focus_force()
                entry_edit.bind(
                    "<Return>", lambda e: hold_new_dice_pattern_info_value(row, col)
                )
                entry_edit.bind(
                    "<FocusOut>", lambda e: hold_new_dice_pattern_info_value(row, col)
                )
            elif col == "#2":
                edit_dice_pattern_pic(int(row))

    def edit_dice_pattern_pic(pattern_id):
        """
        编辑六面骰骰面图片
        参数pattern_id：要编辑的骰面对应的面编号，应为int类型。
        无返回值。
        """

        def hold_new_dice_pattern_pic(pattern_id):
            """
            暂存新六面骰骰面图片
            点击button_confirm后会执行此函数。
            参数pattern_id：要编辑的骰面对应的面编号，应为int类型。
            无返回值。
            """
            nonlocal old_dice_pattern_info, new_dice_pattern_info, new_dice_pattern_info_unsaved_mark
            new_pic_path = entry_new_pattern_pic_file_path.get()
            if len(new_pic_path) < 1:
                label_path_info_tip.config(text="新图片路径为空，请输入新图片路径。")
                return
            if not (os.path.exists(new_pic_path) and os.path.isfile(new_pic_path)):
                label_path_info_tip.config(
                    text="未找到新图片，请检查新图片路径是否正确。"
                )
                return
            dice_pattern_images[pattern_id].config(file=new_pic_path)
            window_dice_info_edit.update()
            new_dice_pattern_pics_path[pattern_id] = new_pic_path
            new_dice_pattern_info_unsaved_mark = True
            update_label_unsaved_mark()
            window_edit_dice_pattern_pic.destroy()

        window_edit_dice_pattern_pic = tkinter.Toplevel(window_dice_info_edit)
        window_edit_dice_pattern_pic.title("编辑骰面图片")
        window_edit_dice_pattern_pic.iconbitmap(PROGRAM_ICON_PATH)
        window_edit_dice_pattern_pic.resizable(False, False)

        label_edit_pattern_id_tip = tkinter.Label(
            window_edit_dice_pattern_pic,
            text="编辑编号为 " + str(pattern_id) + " 的骰面对应的图片          ",
            justify="left",
            font=FONT_NORMAL,
        )
        label_edit_pattern_id_tip.grid(row=0, column=0, columnspan=2, sticky="w")

        label_new_pattern_pic_file_path_indication = tkinter.Label(
            window_edit_dice_pattern_pic,
            text="新图片路径：",
            justify="left",
            font=FONT_NORMAL,
        )
        label_new_pattern_pic_file_path_indication.grid(
            row=1, column=0, columnspan=2, sticky="w"
        )

        entry_new_pattern_pic_file_path = tkinter.Entry(
            window_edit_dice_pattern_pic, width=60, font=FONT_NORMAL
        )
        entry_new_pattern_pic_file_path.grid(row=2, column=0, columnspan=2, sticky="we")

        label_path_info_tip = tkinter.Label(
            window_edit_dice_pattern_pic, text=" ", justify="left", font=FONT_NORMAL
        )
        label_path_info_tip.grid(row=3, column=0, columnspan=2, sticky="w")

        button_cancel = tkinter.Button(
            window_edit_dice_pattern_pic,
            text="取消",
            font=FONT_NORMAL,
            command=window_edit_dice_pattern_pic.destroy,
        )
        button_cancel.grid(row=4, column=0)

        button_confirm = tkinter.Button(
            window_edit_dice_pattern_pic,
            text="确认",
            font=FONT_NORMAL,
            command=lambda: hold_new_dice_pattern_pic(pattern_id),
        )
        button_confirm.grid(row=4, column=1)

    def exit_edit_dice_info():
        """
        关闭编辑六面骰信息窗口
        无返回值。
        """
        global first_level_sub_window_opened
        first_level_sub_window_opened = False
        window_dice_info_edit.destroy()

    def hold_new_dice_description(event):
        """
        暂存新六面骰描述
        当焦点在entry_dice_description上时按“Enter”键或entry_dice_description失去焦点时会执行此函数。
        参数event：当焦点在entry_dice_description上时按“Enter”键的事件或entry_dice_description失去焦点的事件。
        无返回值。
        """
        nonlocal new_dice_description, new_dice_description_unsaved_mark
        new_dice_description = entry_dice_description.get()
        if new_dice_description != active_dice.get_description():
            new_dice_description_unsaved_mark = True
        else:
            new_dice_description_unsaved_mark = False
        update_label_unsaved_mark()

    def hold_new_dice_name(event):
        """
        暂存新六面骰名称
        当焦点在entry_dice_name上时按“Enter”键或entry_dice_name失去焦点时会执行此函数。
        参数event：当焦点在entry_dice_name上时按“Enter”键的事件或entry_dice_name失去焦点的事件。
        无返回值。
        """
        nonlocal new_dice_name, new_dice_name_unsaved_mark
        new_dice_name = entry_dice_name.get()
        if new_dice_name != active_dice.get_name():
            new_dice_name_unsaved_mark = True
        else:
            new_dice_name_unsaved_mark = False
        update_label_unsaved_mark()

    def hold_new_dice_pattern_info_value(row, col):
        """
        暂存新六面骰骰面信息（不包括六面骰骰面图片）
        当焦点在entry_edit上时按“Enter”键或entry_edit失去焦点时会执行此函数，entry_edit为双击treeview_dice_pattern_info上的除了六面骰骰面图片外的可编辑信息后显示的编辑框。
        参数event：当焦点在entry_edit上时按“Enter”键的事件或entry_edit失去焦点的事件。
        无返回值。
        """
        nonlocal entry_edit, old_dice_pattern_info, new_dice_pattern_info, new_dice_pattern_info_unsaved_mark
        new_value = entry_edit.get()
        treeview_dice_pattern_info.set(row, col, new_value)
        row_int = int(row)
        col_int = int(col[1:])
        if col_int == 1:
            new_dice_pattern_info[row_int][0] = new_value
        elif col_int == 3:
            new_dice_pattern_info[row_int][3] = new_value
            new_dice_pattern_info[row_int][2] = eval(new_value)
        else:
            pass
        if len(new_dice_pattern_pics_path) == 0:
            if new_dice_pattern_info != old_dice_pattern_info:
                new_dice_pattern_info_unsaved_mark = True
            else:
                new_dice_pattern_info_unsaved_mark = False
        entry_edit.destroy()
        entry_edit = None
        update_label_unsaved_mark()

    def save_dice_info():
        """
        保存六面骰信息
        点击button_save后会执行此函数。
        无返回值。
        """
        nonlocal new_dice_name_unsaved_mark, new_dice_description_unsaved_mark, new_dice_pattern_info_unsaved_mark, new_dice_pattern_info, old_dice_pattern_info, new_dice_pattern_pics_path
        if new_dice_name_unsaved_mark:
            if default_dice_name == active_dice.get_name():
                set_defult_dice(new_dice_name)
            active_dice.set_name(new_dice_name)
            new_dice_name_unsaved_mark = False
        if new_dice_description_unsaved_mark:
            active_dice.set_description(new_dice_description)
            new_dice_description_unsaved_mark = False
        if new_dice_pattern_info_unsaved_mark:
            if new_dice_pattern_info != old_dice_pattern_info:
                active_dice.set_pattern_info(new_dice_pattern_info)
                old_dice_pattern_info = deepcopy(new_dice_pattern_info)
            if len(new_dice_pattern_pics_path) > 0:
                for pid in new_dice_pattern_pics_path.keys():
                    active_dice.modify_pattern_pic(pid, new_dice_pattern_pics_path[pid])
                new_dice_pattern_pics_path = {}
            new_dice_pattern_info_unsaved_mark = False
        active_dice.write_dice_info_txt()
        update_label_unsaved_mark()

    def update_label_unsaved_mark():
        """
        更新未保存标记
        根据保存标记的情况更新显示的保存情况和button_save的可用性。
        无返回值。
        """
        if (
            new_dice_name_unsaved_mark
            or new_dice_description_unsaved_mark
            or new_dice_pattern_info_unsaved_mark
        ):
            label_unsaved_mark.config(text="存在未保存的更改")
            button_save.config(state="normal")
        else:
            label_unsaved_mark.config(text="没有未保存的更改")
            button_save.config(state="disabled")

    if not first_level_sub_window_opened:
        first_level_sub_window_opened = True

        window_dice_info_edit = tkinter.Toplevel(window_main)
        window_dice_info_edit.title("编辑六面骰信息")
        window_dice_info_edit.iconbitmap(PROGRAM_ICON_PATH)
        window_dice_info_edit.resizable(False, False)
        window_dice_info_edit.protocol("WM_DELETE_WINDOW", exit_edit_dice_info)

        style = tkinter.ttk.Style()
        style.configure("Treeview.Heading", font=FONT_NORMAL)
        style.configure("Treeview", rowheight=102, font=FONT_NORMAL)

        label_dice_name_indication = tkinter.Label(
            window_dice_info_edit, text="六面骰名称：", justify="left", font=FONT_NORMAL
        )
        label_dice_name_indication.grid(row=0, column=0, columnspan=5, sticky="w")

        entry_dice_name = tkinter.Entry(window_dice_info_edit, font=FONT_NORMAL)
        entry_dice_name.grid(row=1, column=0, columnspan=5, sticky="we")
        entry_dice_name.insert(0, active_dice.get_name())
        entry_dice_name.bind("<Return>", hold_new_dice_name)
        entry_dice_name.bind("<FocusOut>", hold_new_dice_name)
        new_dice_name = active_dice.get_name()
        new_dice_name_unsaved_mark = False

        label_dice_description_indication = tkinter.Label(
            window_dice_info_edit, text="六面骰描述：", justify="left", font=FONT_NORMAL
        )
        label_dice_description_indication.grid(
            row=2, column=0, columnspan=5, sticky="w"
        )

        entry_dice_description = tkinter.Entry(window_dice_info_edit, font=FONT_NORMAL)
        entry_dice_description.grid(row=3, column=0, columnspan=5, sticky="we")
        entry_dice_description.insert(0, active_dice.get_description())
        entry_dice_description.bind("<Return>", hold_new_dice_description)
        entry_dice_description.bind("<FocusOut>", hold_new_dice_description)
        new_dice_description = active_dice.get_description()
        new_dice_description_unsaved_mark = False

        label_dice_pattern_info_indication = tkinter.Label(
            window_dice_info_edit,
            text="六面骰骰面信息：",
            justify="left",
            font=FONT_NORMAL,
        )
        label_dice_pattern_info_indication.grid(
            row=4, column=0, columnspan=5, sticky="w"
        )

        treeview_dice_pattern_info = tkinter.ttk.Treeview(
            window_dice_info_edit,
            columns=("面名称", "面图案", "面掷出概率信息"),
            height=6,
        )
        treeview_dice_pattern_info.grid(row=5, column=0, columnspan=5, sticky="w")
        treeview_dice_pattern_info.heading("#0", text="面编号")
        treeview_dice_pattern_info.heading("#1", text="面名称")
        treeview_dice_pattern_info.heading("#2", text="面图案")
        treeview_dice_pattern_info.heading("#3", text="面掷出概率信息")
        treeview_dice_pattern_info.column(column="#0", width=100, anchor=tkinter.CENTER)
        treeview_dice_pattern_info.column(
            column="面名称", width=200, anchor=tkinter.CENTER
        )
        treeview_dice_pattern_info.column(
            column="面图案", width=200, anchor=tkinter.CENTER
        )
        treeview_dice_pattern_info.column(
            column="面掷出概率信息", width=200, anchor=tkinter.CENTER
        )
        old_dice_pattern_info = active_dice.get_pattern_info()
        new_dice_pattern_info = deepcopy(old_dice_pattern_info)
        active_dice_folder_path = active_dice.get_folder_path()
        for i in range(1, 7):
            treeview_dice_pattern_info.insert(
                "",
                "end",
                iid=str(i),
                text=str(i),
                values=(new_dice_pattern_info[i][0], "", new_dice_pattern_info[i][3]),
            )
        window_dice_info_edit.update()
        for i in range(1, 7):
            x, y, w, h = treeview_dice_pattern_info.bbox(str(i), "面图案")
            dice_pattern_images[i] = tkinter.PhotoImage(
                file=active_dice_folder_path + "/" + new_dice_pattern_info[i][1]
            )
            label_dice_pattern_pic = tkinter.Label(
                treeview_dice_pattern_info, image=dice_pattern_images[i], justify="left"
            )
            label_dice_pattern_pic.place(x=x + ((w - 100) / 2), y=y)
            label_dice_pattern_pic.bind("<Double-1>", double_click_pic_edit)
        treeview_dice_pattern_info.bind(
            "<Motion>", "break"
        )  # 禁用treeview_dice_pattern_info列宽的鼠标拖动调整
        treeview_dice_pattern_info.bind("<Double-1>", double_click_treeview_edit)
        entry_edit = None
        new_dice_pattern_pics_path = {}
        new_dice_pattern_info_unsaved_mark = False

        label_edit_info_tip = tkinter.Label(
            window_dice_info_edit,
            text="注意：文本内容编辑后需要按“Enter”键或点击其他可编辑内容以提交修改。",
            justify="left",
            font=FONT_NORMAL,
        )
        label_edit_info_tip.grid(row=6, column=0, columnspan=5, sticky="w")

        label_unsaved_mark = tkinter.Label(
            window_dice_info_edit,
            text="没有未保存的更改",
            justify="left",
            font=FONT_NORMAL,
        )
        label_unsaved_mark.grid(row=7, column=0, columnspan=5, sticky="w")

        button_cancel = tkinter.Button(
            window_dice_info_edit,
            text="取消",
            font=FONT_NORMAL,
            command=exit_edit_dice_info,
        )
        button_cancel.grid(row=8, column=1)

        button_save = tkinter.Button(
            window_dice_info_edit,
            text="保存",
            font=FONT_NORMAL,
            state="disabled",
            command=save_dice_info,
        )
        button_save.grid(row=8, column=2)

        button_confirm = tkinter.Button(
            window_dice_info_edit,
            text="确定",
            font=FONT_NORMAL,
            command=confirm_dice_info,
        )
        button_confirm.grid(row=8, column=3)

def button_settings_operation():

    global first_level_sub_window_opened

    def exit_settings():
        """
        关闭设置窗口
        无返回值。
        """
        global first_level_sub_window_opened
        first_level_sub_window_opened = False
        window_settings.destroy()

    def button_save_settings_operation():

        def forced_save_settings():
            window_unowned_default_dice_confirm.destroy()
            save_settings()

        def save_settings():
            with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(SETTINGS_FILE_HEAD)
                f.write("\n\n")
                f.write("默认六面骰：" + default_dice_name)
                f.write("\n\n")
            exit_settings()

        default_dice_name = entry_default_dice.get()
        if default_dice_name not in dice_bag.keys():
            window_unowned_default_dice_confirm = tkinter.Toplevel(window_settings)
            window_unowned_default_dice_confirm.title(
                "将未拥有的六面骰设置为默认六面骰的确认"
            )
            window_unowned_default_dice_confirm.iconbitmap(PROGRAM_ICON_PATH)
            window_unowned_default_dice_confirm.resizable(False, False)

            label_unowned_default_dice_tip_cover_dice_name = tkinter.Label(
                window_unowned_default_dice_confirm,
                text="当前六面骰包中没有名称为 "
                + default_dice_name
                + " 的骰子，\n确定要将 "
                + default_dice_name
                + " 设置为默认六面骰吗？",
                justify="left",
                font=FONT_NORMAL,
            )
            label_unowned_default_dice_tip_cover_dice_name.grid(
                row=0, column=0, columnspan=2, sticky="w"
            )

            label_discard_dice_tip_common = tkinter.Label(
                window_unowned_default_dice_confirm,
                text="若启动六面骰模拟器之后在六面骰包中没有找到默认六面骰，\n则六面骰模拟器会进入没有正在使用的六面骰的状态。",
                justify="left",
                font=FONT_NORMAL,
            )
            label_discard_dice_tip_common.grid(
                row=1, column=0, columnspan=2, sticky="w"
            )

            button_cancel = tkinter.Button(
                window_unowned_default_dice_confirm,
                text="取消",
                font=FONT_NORMAL,
                command=window_unowned_default_dice_confirm.destroy,
            )
            button_cancel.grid(row=2, column=0)

            button_confirm = tkinter.Button(
                window_unowned_default_dice_confirm,
                text="确认",
                font=FONT_NORMAL,
                command=forced_save_settings,
            )
            button_confirm.grid(row=2, column=1)
        else:
            save_settings()

    if not first_level_sub_window_opened:
        first_level_sub_window_opened = True

        window_settings = tkinter.Toplevel(window_main)
        window_settings.title("设置")
        window_settings.iconbitmap(PROGRAM_ICON_PATH)
        window_settings.resizable(False, False)
        window_settings.protocol("WM_DELETE_WINDOW", exit_settings)

        label_default_dice_indication = tkinter.Label(
            window_settings, text="默认六面骰：", justify="left", font=FONT_NORMAL
        )
        label_default_dice_indication.grid(row=0, column=0, columnspan=2, sticky="w")

        entry_default_dice = tkinter.Entry(window_settings, font=FONT_NORMAL)
        entry_default_dice.grid(row=1, column=0, columnspan=2, sticky="we")
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            default_dice_name = f.readline()[:-1].split("：")[1]
            entry_default_dice.insert(0, default_dice_name)

        label_default_dice_tip = tkinter.Label(
            window_settings,
            text=DEFAULT_DICE_TIP,
            justify="left",
            wraplength=450,
            font=FONT_NORMAL,
        )
        label_default_dice_tip.grid(row=2, column=0, columnspan=2, sticky="w")

        button_save_settings = tkinter.Button(
            window_settings,
            text="保存设置",
            width=10,
            font=FONT_NORMAL,
            command=button_save_settings_operation,
        )
        button_save_settings.grid(row=3, column=0)

        button_cancel = tkinter.Button(
            window_settings,
            text="取消",
            width=10,
            font=FONT_NORMAL,
            command=exit_settings,
        )
        button_cancel.grid(row=3, column=1)

def button_switch_dice_operation():

    global first_level_sub_window_opened

    def button_add_dice_operation():
        """
        打开输入将要新添加的六面骰的文件路径的窗口
        点击button_add_new_dice后会执行此函数。
        无返回值。
        """

        def add_new_dice():
            """
            添加新六面骰到六面骰包
            点击button_confirm后会执行此函数。
            无返回值。
            """
            new_dice_path = entry_new_dice_folder_path.get()
            if len(new_dice_path) < 1:
                label_path_info_tip.config(
                    text="新六面骰文件路径为空，请输入新图片路径。"
                )
                return
            if (not os.path.exists(new_dice_path)) or os.path.isfile(new_dice_path):
                label_path_info_tip.config(
                    text="未找到新六面骰文件，请检查新图片路径是否正确。"
                )
                return
            if len(dice_bag) >= DICE_BAG_CAPACITY:
                label_path_info_tip.config(
                    text="无法添加新六面骰，因为六面骰包中最多只能容纳 "
                    + str(DICE_BAG_CAPACITY)
                    + " 个六面骰"
                )
                return
            if os.path.basename(new_dice_path) in dice_bag.keys():
                label_path_info_tip.config(
                    text="无法添加新六面骰，因为六面骰包中存在同名的六面骰。"
                )
                return
            add_dice_feedback = add_dice_to_bag(new_dice_path)
            if not add_dice_feedback[0]:
                label_path_info_tip.config(
                    text="无法添加新六面骰。原因：" + add_dice_feedback[1]
                )
                return
            window_add_new_dice.destroy()
            update_listbox_dice_bag()

        window_add_new_dice = tkinter.Toplevel(window_switch_dice)
        window_add_new_dice.title("添加新六面骰")
        window_add_new_dice.iconbitmap(PROGRAM_ICON_PATH)
        window_add_new_dice.resizable(False, False)

        label_add_new_dice_tip = tkinter.Label(
            window_add_new_dice, text="添加新六面骰", justify="left", font=FONT_NORMAL
        )
        label_add_new_dice_tip.grid(row=0, column=0, columnspan=2, sticky="w")

        label_new_dice_folder_path_indication = tkinter.Label(
            window_add_new_dice,
            text="新六面骰文件夹路径：",
            justify="left",
            font=FONT_NORMAL,
        )
        label_new_dice_folder_path_indication.grid(
            row=1, column=0, columnspan=2, sticky="w"
        )

        entry_new_dice_folder_path = tkinter.Entry(
            window_add_new_dice, width=60, font=FONT_NORMAL
        )
        entry_new_dice_folder_path.grid(row=2, column=0, columnspan=2, sticky="we")

        label_path_info_tip = tkinter.Label(
            window_add_new_dice, text=" ", justify="left", font=FONT_NORMAL
        )
        label_path_info_tip.grid(row=3, column=0, columnspan=2, sticky="w")

        button_cancel = tkinter.Button(
            window_add_new_dice,
            text="取消",
            font=FONT_NORMAL,
            command=window_add_new_dice.destroy,
        )
        button_cancel.grid(row=4, column=0)

        button_confirm = tkinter.Button(
            window_add_new_dice, text="确认", font=FONT_NORMAL, command=add_new_dice
        )
        button_confirm.grid(row=4, column=1)

    def button_discard_dice_operation():
        """
        打开丢弃六面骰确认窗口
        点击button_discard_dice后会执行此函数。
        无返回值。
        """

        def discard_dice():
            """
            丢弃六面骰
            点击button_confirm后会执行此函数。
            无返回值。
            """
            global active_dice
            if active_dice and active_dice.get_name() == discard_dice_name:
                active_dice = None
                update_window_main_info()
            del dice_bag[discard_dice_name]
            shutil.rmtree(DICE_FOLDER_PATH + "/" + discard_dice_name)
            update_listbox_dice_bag()
            button_discard_dice.config(state="disabled")
            window_discard_dice_warn.destroy()

        if (
            len(listbox_dice_bag.curselection()) > 0
        ):  # 避免点击button_discard_dice后listbox_dice_bag.curselection()返回空元组而产生报错
            discard_dice_name = listbox_dice_bag.get(listbox_dice_bag_active_index)

            window_discard_dice_warn = tkinter.Toplevel(window_switch_dice)
            window_discard_dice_warn.title("删除六面骰确认")
            window_discard_dice_warn.iconbitmap(PROGRAM_ICON_PATH)
            window_discard_dice_warn.resizable(False, False)

            label_discard_dice_tip_cover_dice_name = tkinter.Label(
                window_discard_dice_warn,
                text="确定要删除 " + discard_dice_name + " 吗？",
                justify="left",
                font=FONT_NORMAL,
            )
            label_discard_dice_tip_cover_dice_name.grid(
                row=0, column=0, columnspan=2, sticky="w"
            )

            label_discard_dice_tip_common = tkinter.Label(
                window_discard_dice_warn,
                text="这会删除存储该六面骰信息的文件，此操作不可逆，请谨慎决定。",
                justify="left",
                font=FONT_NORMAL,
            )
            label_discard_dice_tip_common.grid(
                row=1, column=0, columnspan=2, sticky="w"
            )

            button_cancel = tkinter.Button(
                window_discard_dice_warn,
                text="取消",
                font=FONT_NORMAL,
                command=window_discard_dice_warn.destroy,
            )
            button_cancel.grid(row=2, column=0)

            button_confirm = tkinter.Button(
                window_discard_dice_warn,
                text="确认",
                font=FONT_NORMAL,
                command=discard_dice,
            )
            button_confirm.grid(row=2, column=1)

    def exit_switch_dice():
        """
        关闭切换六面骰窗口
        无返回值。
        """
        global first_level_sub_window_opened
        first_level_sub_window_opened = False
        window_switch_dice.destroy()

    def listbox_dice_bag_select(event):
        """
        六面骰包列表框选择
        当listbox_dice_bag中的项目被选取时会执行此函数。
        参数event：listbox_dice_bag中的项目被选取的事件。
        无返回值。
        """
        if (
            len(listbox_dice_bag.curselection()) > 0
        ):  # 避免选取Entry内容时发送<<ListboxSelect>>而listbox_dice_bag.curselection()返回空元组而产生报错
            nonlocal listbox_dice_bag_active_index
            listbox_dice_bag_active_index = listbox_dice_bag.curselection()[0]
            stringvar_dice_name.set(listbox_dice_bag.get(listbox_dice_bag_active_index))
            stringvar_dice_description.set(
                dice_bag[
                    listbox_dice_bag.get(listbox_dice_bag_active_index)
                ].get_description()
            )
            button_discard_dice.config(state="normal")

    def button_confirm_operation():
        """
        确定使用选定的六面骰
        点击button_confirm后会执行此函数。此函数会将当前listbox_dice_bag中选择的六面骰设置为当前使用的六面骰（active_dice），并关闭切换六面骰窗口。
        无返回值。
        """
        if (
            len(listbox_dice_bag.curselection()) > 0
        ):  # 避免没有选择listbox_dice_bag中的任何一个条目时点击button_confirm后报错
            listbox_dice_bag_active_index = listbox_dice_bag.curselection()[0]
            new_active_dice_name = listbox_dice_bag.get(listbox_dice_bag_active_index)
            switch_active_dice(new_active_dice_name)
        exit_switch_dice()

    def update_listbox_dice_bag():
        """
        更新六面骰包列表框
        此函数根据当前dice_bag中的信息更新六面骰包列表框中的条目。
        无返回值。
        """
        nonlocal listbox_dice_bag_active_index
        listbox_dice_bag.delete(0, tkinter.END)
        listbox_dice_bag_i = 0
        listbox_dice_bag_active_index = -1
        for dice in dice_bag.keys():
            listbox_dice_bag.insert(listbox_dice_bag_i, dice)
            if active_dice and dice == active_dice.get_name():
                listbox_dice_bag_active_index = listbox_dice_bag_i
            listbox_dice_bag_i += 1
        if active_dice:
            listbox_dice_bag.selection_set(listbox_dice_bag_active_index)

    if not first_level_sub_window_opened:
        first_level_sub_window_opened = True

        window_switch_dice = tkinter.Toplevel(window_main)
        window_switch_dice.title("切换六面骰")
        window_switch_dice.iconbitmap(PROGRAM_ICON_PATH)
        window_switch_dice.resizable(False, False)
        window_switch_dice.protocol("WM_DELETE_WINDOW", exit_switch_dice)

        label_dice_bag_indication = tkinter.Label(
            window_switch_dice, text="六面骰包：", justify="left", font=FONT_NORMAL
        )
        label_dice_bag_indication.grid(row=0, column=0, columnspan=6, sticky="w")

        listbox_dice_bag = tkinter.Listbox(
            window_switch_dice, height=DICE_BAG_CAPACITY, width=80, font=FONT_NORMAL
        )
        listbox_dice_bag.grid(row=1, column=0, columnspan=6, sticky="we")
        listbox_dice_bag.bind("<<ListboxSelect>>", listbox_dice_bag_select)
        listbox_dice_bag_active_index = -1
        update_listbox_dice_bag()

        label_dice_name_indication = tkinter.Label(
            window_switch_dice, text="六面骰名称：", justify="left", font=FONT_NORMAL
        )
        label_dice_name_indication.grid(row=3, column=0, columnspan=6, sticky="w")

        stringvar_dice_name = tkinter.StringVar()
        entry_dice_name = tkinter.Entry(
            window_switch_dice, textvariable=stringvar_dice_name, font=FONT_NORMAL
        )
        entry_dice_name.grid(row=4, column=0, columnspan=6, sticky="we")
        if active_dice:
            stringvar_dice_name.set(
                dice_bag[listbox_dice_bag.get(listbox_dice_bag_active_index)].get_name()
            )
        entry_dice_name.config(state="readonly")

        label_dice_description_indication = tkinter.Label(
            window_switch_dice, text="六面骰描述：", justify="left", font=FONT_NORMAL
        )
        label_dice_description_indication.grid(
            row=5, column=0, columnspan=6, sticky="w"
        )

        stringvar_dice_description = tkinter.StringVar()
        entry_dice_description = tkinter.Entry(
            window_switch_dice,
            textvariable=stringvar_dice_description,
            font=FONT_NORMAL,
        )
        entry_dice_description.grid(row=6, column=0, columnspan=6, sticky="we")
        if active_dice:
            stringvar_dice_description.set(
                dice_bag[
                    listbox_dice_bag.get(listbox_dice_bag_active_index)
                ].get_description()
            )
        entry_dice_description.config(state="readonly")

        button_add_dice = tkinter.Button(
            window_switch_dice,
            width=10,
            text="添加骰子",
            font=FONT_NORMAL,
            command=button_add_dice_operation,
        )
        button_add_dice.grid(row=7, column=1)

        button_discard_dice = tkinter.Button(
            window_switch_dice,
            width=10,
            text="丢弃骰子",
            font=FONT_NORMAL,
            state="disabled",
            command=button_discard_dice_operation,
        )
        button_discard_dice.grid(row=7, column=2)
        if listbox_dice_bag_active_index >= 0:
            button_discard_dice.config(state="normal")

        button_confirm = tkinter.Button(
            window_switch_dice,
            width=10,
            text="确定",
            font=FONT_NORMAL,
            command=button_confirm_operation,
        )
        button_confirm.grid(row=7, column=3)

        button_cancel = tkinter.Button(
            window_switch_dice,
            width=10,
            text="取消",
            font=FONT_NORMAL,
            command=exit_switch_dice,
        )
        button_cancel.grid(row=7, column=4)

def button_throw_dice_operation():
    active_dice.throw()
    show_dice_state()

def button_show_dice_info_operation():

    global first_level_sub_window_opened

    def exit_show_dice_info():
        """
        关闭六面骰信息窗口
        无返回值。
        """
        global first_level_sub_window_opened
        first_level_sub_window_opened = False
        window_dice_info_show.destroy()

    if not first_level_sub_window_opened:
        first_level_sub_window_opened = True

        window_dice_info_show = tkinter.Toplevel(window_main)
        window_dice_info_show.title("六面骰信息")
        window_dice_info_show.iconbitmap(PROGRAM_ICON_PATH)
        window_dice_info_show.resizable(False, False)
        window_dice_info_show.protocol("WM_DELETE_WINDOW", exit_show_dice_info)

        style = tkinter.ttk.Style()
        style.configure("Treeview.Heading", font=FONT_NORMAL)
        style.configure("Treeview", rowheight=102, font=FONT_NORMAL)

        label_dice_name = tkinter.Label(
            window_dice_info_show,
            text="六面骰名称：\n" + active_dice.get_name(),
            justify="left",
            font=FONT_NORMAL,
        )
        label_dice_name.grid(row=0, column=0, sticky="w")

        label_dice_description = tkinter.Label(
            window_dice_info_show,
            text="六面骰描述：\n" + active_dice.get_description(),
            justify="left",
            font=FONT_NORMAL,
        )
        label_dice_description.grid(row=1, column=0, sticky="w")

        label_dice_pattern_info_indication = tkinter.Label(
            window_dice_info_show,
            text="六面骰骰面信息：",
            justify="left",
            font=FONT_NORMAL,
        )
        label_dice_pattern_info_indication.grid(row=2, column=0, sticky="w")

        treeview_dice_pattern_info = tkinter.ttk.Treeview(
            window_dice_info_show,
            columns=("面名称", "面图案", "面掷出概率信息"),
            height=6,
        )
        treeview_dice_pattern_info.grid(row=3, column=0, sticky="w")
        treeview_dice_pattern_info.heading("#0", text="面编号")
        treeview_dice_pattern_info.heading("#1", text="面名称")
        treeview_dice_pattern_info.heading("#2", text="面图案")
        treeview_dice_pattern_info.heading("#3", text="面掷出概率信息")
        treeview_dice_pattern_info.column(column="#0", width=100, anchor=tkinter.CENTER)
        treeview_dice_pattern_info.column(column="面名称", anchor=tkinter.CENTER)
        treeview_dice_pattern_info.column(column="面图案", anchor=tkinter.CENTER)
        treeview_dice_pattern_info.column(
            column="面掷出概率信息", anchor=tkinter.CENTER
        )
        active_dice_pattern_info = active_dice.get_pattern_info()
        active_dice_folder_path = active_dice.get_folder_path()
        for i in range(1, 7):
            treeview_dice_pattern_info.insert(
                "",
                "end",
                iid=str(i),
                text=str(i),
                values=(
                    active_dice_pattern_info[i][0],
                    "",
                    active_dice_pattern_info[i][3],
                ),
            )
        window_dice_info_show.update()
        for i in range(1, 7):
            x, y, w, h = treeview_dice_pattern_info.bbox(str(i), "面图案")
            dice_pattern_images[i] = tkinter.PhotoImage(
                file=active_dice_folder_path + "/" + active_dice_pattern_info[i][1]
            )
            label_dice_pattern_pic = tkinter.Label(
                treeview_dice_pattern_info, image=dice_pattern_images[i], justify="left"
            )
            label_dice_pattern_pic.place(x=x + ((w - 100) / 2), y=y)
        treeview_dice_pattern_info.bind(
            "<Motion>", "break"
        )  # 禁用treeview_dice_pattern_info列宽的鼠标拖动调整

        button_confirm = tkinter.Button(
            window_dice_info_show,
            text="确定",
            font=FONT_NORMAL,
            command=exit_show_dice_info,
        )
        button_confirm.grid(row=4, column=0)

def set_defult_dice(new_defult_dice_name):
    """
    修改默认六面骰
    本函数会修改default_dice_name的值并重写设置文件。
    参数new_defult_dice_name：新默认六面骰的名称。
    无返回值
    """
    global default_dice_name
    default_dice_name = new_defult_dice_name
    write_setting_file()

def show_dice_state():
    """
    展示六面骰状态
    在六面骰模拟器主窗口上展示当前使用的六面骰的当前状态，
    注意本函数不会更新主窗口上当前使用六面骰的名称。
    无返回值。
    """
    currnet_dice_pattern_image.config(
        file=active_dice.get_currnet_pattern_pic_file_path()
    )
    label_dice_pattern_pic.config(image=currnet_dice_pattern_image)
    label_dice_pattern_name.config(
        text="当前掷出面名称：" + active_dice.get_current_pattern_name()
    )

def switch_active_dice(new_active_dice_name):
    """
    切换当前使用的六面骰
    参数new_active_dice_name：将要使用的六面骰名称。该名称对应的六面骰对象需要已经在dice_bag中。
    无返回值。
    """
    global active_dice
    active_dice = dice_bag[new_active_dice_name]
    update_window_main_info()

def update_window_main_info():
    """
    更新主窗口
    此函数将根据当前使用的六面骰更新window_main上展示的信息。
    无返回值。
    """
    if active_dice == None:
        label_dice_name.config(text="当前使用的六面骰：")
        currnet_dice_pattern_image.config(file=NULL_PATTERN_PIC_PATH)
        label_dice_pattern_pic.config(image=currnet_dice_pattern_image)
        label_dice_pattern_name.config(text="当前掷出面名称：")
        label_main_tip.config(text=NULL_ACTIVE_DICE_TIP)
        button_throw_dice.config(state="disabled")
        button_show_dice_info.config(state="disabled")
        button_edit_dice_info.config(state="disabled")
    else:
        label_dice_name.config(text="当前使用的六面骰：" + active_dice.get_name())
        show_dice_state()
        label_main_tip.config(text=" ")
        button_throw_dice.config(state="normal")
        button_show_dice_info.config(state="normal")
        button_edit_dice_info.config(state="normal")

def write_setting_file():
    """
    写入设置信息文件
    将当前设置信息写入设置信息文件，将会覆盖旧的设置信息文件。
    无返回值。
    """
    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(SETTINGS_FILE_HEAD)
        f.write("\n\n")
        f.write("默认六面骰：" + default_dice_name)
        f.write("\n")


if __name__ == "__main__":
    # 检查在当前工作文件夹下是否有正在运行的其他Sixsided Dice Simulator实例
    if os.path.exists(PROGRAM_SINGLE_INSTANCE_LOCK_FILE_PATH):
        before_main_error_window = tkinter.Tk()
        before_main_error_window.title("六面骰模拟器")
        before_main_error_window.iconbitmap(PROGRAM_ICON_PATH)
        before_main_error_window.geometry("500x160")
        before_main_error_window.resizable(False, False)
        tkinter.Label(
            before_main_error_window, image="::tk::icons::error", width=50, height=50
        ).grid(row=0, column=0)
        tkinter.Label(
            before_main_error_window,
            text="当前在该工作文件夹下已经存在一个正在运行的六面骰模拟器。",
            wraplength=440,
            justify="left",
            font=FONT_IMPORTANT,
        ).grid(row=0, column=1)
        tkinter.Label(
            before_main_error_window,
            text="工作文件夹相同的六面骰模拟器只允许有一个正在运行的实例，请使用正在运行的实例或结束正在运行的实例后再启动新六面骰模拟器实例。",
            wraplength=450,
            justify="left",
            font=FONT_NORMAL,
        ).grid(row=2, column=0, columnspan=2)
        tkinter.mainloop()
        sys.exit(1)
    else:
        build_file_lock = True
        with open(
            PROGRAM_SINGLE_INSTANCE_LOCK_FILE_PATH, "w", encoding="utf-8"
        ) as lock_file:
            lock_file.write(str(os.getpid()))

    if not os.path.exists(DICE_FOLDER_PATH):
        os.mkdir(DICE_FOLDER_PATH)

    # 创建六面骰包并加载六面骰
    dice_bag = {}
    for f in os.listdir(DICE_FOLDER_PATH):
        if len(dice_bag) > DICE_BAG_CAPACITY:
            break
        if not os.path.isfile(f):
            dice_bag[f] = Dice(f)

    active_dice = None

    if os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            default_dice_name = f.readline()[:-1].split("：")[1]
            if default_dice_name in dice_bag.keys():
                active_dice = dice_bag[default_dice_name]
    else:
        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(SETTINGS_FILE_HEAD)
            f.write("\n\n")
            f.write("默认六面骰：")
            f.write("\n\n")

    window_main = tkinter.Tk()
    window_main.title(PROGRAM_NAME)
    window_main.iconbitmap(PROGRAM_ICON_PATH)
    # 通过button_show_dice_info和button_edit_dice_info的宽度控制主窗口宽度
    window_main.geometry("500x450")
    window_main.resizable(False, False)

    dice_pattern_images = {}
    program_icon_image = tkinter.PhotoImage(file=PROGRAM_ICON_PNG_PATH)

    frame_top_part = tkinter.Frame(window_main)
    frame_top_part.pack(side="top")

    label_dice_name = tkinter.Label(
        frame_top_part, text="当前使用的六面骰：", justify="left", font=FONT_NORMAL
    )
    label_dice_name.grid(row=0, column=0, columnspan=2, sticky="w")

    currnet_dice_pattern_image = tkinter.PhotoImage(file=NULL_PATTERN_PIC_PATH)
    label_dice_pattern_pic = tkinter.Label(
        frame_top_part, image=currnet_dice_pattern_image, justify="left"
    )
    label_dice_pattern_pic.grid(row=1, column=0)

    button_throw_dice = tkinter.Button(
        frame_top_part,
        text="掷骰子",
        font=FONT_IMPORTANT,
        state="disabled",
        command=button_throw_dice_operation,
    )
    button_throw_dice.grid(row=1, column=1, rowspan=2, sticky="we", padx=20, pady=20)

    label_dice_pattern_name = tkinter.Label(
        frame_top_part, text="当前掷出面名称：", justify="left", font=FONT_NORMAL
    )
    label_dice_pattern_name.grid(row=2, column=0, columnspan=2, sticky="w")

    label_main_tip = tkinter.Label(
        frame_top_part,
        text=NULL_ACTIVE_DICE_TIP,
        justify="left",
        wraplength=500,
        font=FONT_NORMAL,
    )
    label_main_tip.grid(row=3, column=0, columnspan=2, sticky="w")

    label_frame_top_part_width_ctrl = tkinter.Label(
        frame_top_part,
        text=(" " * 124),
        justify="left",
        wraplength=500,
        font=FONT_NORMAL,
    )
    label_frame_top_part_width_ctrl.grid(row=4, column=0, columnspan=2, sticky="w")

    first_level_sub_window_opened = False

    frame_bottom_part = tkinter.Frame(window_main)
    frame_bottom_part.pack(side="bottom")
    frame_bottom_part.columnconfigure(0, minsize=200)
    frame_bottom_part.columnconfigure(1, minsize=200)

    button_show_dice_info = tkinter.Button(
        frame_bottom_part,
        text="查看骰子信息",
        font=FONT_NORMAL,
        state="disabled",
        command=button_show_dice_info_operation,
    )
    button_show_dice_info.grid(row=0, column=0, sticky="we", padx=5, pady=5)

    button_edit_dice_info = tkinter.Button(
        frame_bottom_part,
        text="编辑骰子信息",
        font=FONT_NORMAL,
        state="disabled",
        command=button_edit_dice_info_operation,
    )
    button_edit_dice_info.grid(row=0, column=1, sticky="we", padx=5, pady=5)

    button_switch_dice = tkinter.Button(
        frame_bottom_part,
        text="切换骰子",
        font=FONT_NORMAL,
        command=button_switch_dice_operation,
    )
    button_switch_dice.grid(row=1, column=0, sticky="we", padx=5, pady=5)

    button_settings = tkinter.Button(
        frame_bottom_part,
        text="设置",
        font=FONT_NORMAL,
        command=button_settings_operation,
    )
    button_settings.grid(row=1, column=1, sticky="we", padx=5, pady=5)

    button_about = tkinter.Button(
        frame_bottom_part, text="关于", font=FONT_NORMAL, command=button_about_operation
    )
    button_about.grid(row=2, column=0, sticky="we", padx=5, pady=5)

    button_exit = tkinter.Button(
        frame_bottom_part, text="退出", font=FONT_NORMAL, command=window_main.destroy
    )
    button_exit.grid(row=2, column=1, sticky="we", padx=5, pady=5)

    update_window_main_info()

    # print(window_main.winfo_screenwidth())  #输出显示器逻辑宽度
    # print(window_main.winfo_screenheight())  #输出显示器逻辑高度

    tkinter.mainloop()

