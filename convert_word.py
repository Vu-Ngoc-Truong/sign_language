#!/usr/bin/env python3
# -*- coding: utf-8 -*-
char_table = "ô ố ồ ổ ỗ ộ"
list_voxel = [ "a", "ă", "â", "e", "ê", "o", "ô", "ơ", "i", "u", "ư", "y"]
list_voxel_split = [ "a", "aw", "a^", "e", "e^", "o", "o^", "ow", "i", "u", "uw", "y", "đ"]
dict_voxel_rau = {"a": "ă", "o": "ơ", "u": "ư"}
dict_voxel_mu  = {"a": "â", "o": "ô", "e": "ê"}

list_sign = ["'", "`","?", "~", "*" ]
list_dau = "aáàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệoóòỏõọôốồổỗộơớờởỡợiíìỉĩịuúùủũụưứừửữựyýỳỷỹỵđ"
txt = "con chó cắn mỗi đêm dài"

def word_to_char( text =str()):
    """convert from vietnam word to char

    Args:
        text (string, optional): word need convert . Defaults to str().

    Returns:
        string: string result
    """
    lower_text = text.lower()
    list_char = ""
    for c in lower_text:
        if ord(c)<128:
            list_char += c
            continue
        index = list_dau.find(c)
        # print(index)
        if not index == -1:
            i = int(index/6)
            j = int(index%6)
            # print("i, j ", i , j)
            list_char +=list_voxel_split[i]
            # print(list_voxel[i])
            if j >= 1:
                list_char += list_sign[j-1]

    return list_char

def char_to_word( end_char, new_char):
    """ Convert from char to word
        end_char (list): char in end of string
        new_char (string): char want to connect with list of string
        return (string): string
    """
    input_text = []
    input_text.append(end_char)
    print("input text: ", input_text)

    input_char = new_char

    char = input_char[0]
    # get last char

    last_char = input_text[-1]
    print("last char: ", last_char)

    # Check w and ^
    if char == "w":
        if last_char in dict_voxel_rau:
            input_text[-1] = dict_voxel_rau[last_char]

    elif char == "^":
        if last_char in dict_voxel_mu:
            input_text[-1] = dict_voxel_mu[last_char]
    elif char in list_sign:
        id = list_sign.index(char)
        print("dau id:", id)
        if last_char in list_dau:
            id_char = list_dau.find(last_char)
            print("last char id:", id_char)
            input_text[-1] = list_dau[id_char + id + 1]
    else:
        input_text.append(char)
    return input_text

if __name__ == '__main__':
    # print(word_to_char(txt))
    strings = "Ho^m awn"
    list_string = [""]
    for char in strings:

        str_result =  char_to_word(list_string[-1], char)
        print("str result: ", str_result)
        # bo ky tu cuoi
        if len(str_result) == 1:
            list_string[-1] = str_result[0]
        else:
            list_string[-1] = str_result[0]
            list_string.append(str_result[1])
        print("list string:", list_string)
    print("list string end :", list_string)
    input_string =""
    for c in list_string:
        input_string += c
    print("input string: ",input_string)
