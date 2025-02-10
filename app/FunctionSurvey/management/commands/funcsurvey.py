from django.core.management.base import BaseCommand
from ...models import Function, FunctionRelation
from ...survey import Survey

import logging
import csv
import pathlib
import shlex
import clang.cindex

logger = logging.getLogger('FunctionSurvey')

FunctionDeclear = {}
AnalysedFunctionList = []

class FunctionDecl:
    """関数解析クラス
    """    
    def __init__(self, FunctionName:str):
        """初期化

        Args:
            FunctionName (str): 関数名
        """        
        self.Location = ""
        self.FunctionName = FunctionName
        self.FunctionType = "void"
        self.Args = []
        self.ReturnType = {}
        self.CallFunctions = []
        self.StorageClass = None
        self.Status = {
            "戻り値"	    : "void型",    # void型, データ型, ポインタ型
            "引数"	        : "void型",    # void型, データ型, ポインタ型含, voidポインタ型含
            "for"	        : "－",        # ○,－
            "if"	        : "－",        # ○,－
            "switch"	    : "－",        # ○,－
            "while"	        : "－",        # ○,－
            "call_extern"	: "－",        # ○,－
            "call_static"	: "－",        # ○,－
            "other"	        : "－",        # データセット処理のみ,無限ループあり,volatile変数あり,－
        }

        self.IncludeVolatile = False
        self.IncludeBranch = False

    def AddArg(self, cursor:clang.cindex.Cursor):
        """関数引数追加

        Args:
            cursor (clang.cindex.Cursor): 要素カーソル
        """        
        self.Args.append({
            "Type"  : cursor.type.spelling,
            "CanonicalType"  : cursor.type.get_canonical().spelling,
            "Kind"  : cursor.type.kind.name,
            "Name"  : cursor.spelling
        })

    def GetArgs(self) -> list:
        """関数引数取得

        Returns:
            list: 引数リスト
        """        
        return self.Args

    def SetReturnType(self, cursor:clang.cindex.Cursor):
        self.ReturnType = {
            "Type"  : cursor.result_type.spelling,
            "CanonicalType"  : cursor.result_type.get_canonical().spelling,
            "Kind"  : cursor.type.kind.name,
        }

    def GetReturnType(self) -> dict:
        return self.ReturnType

    def AddCallFunction(self, cursor:clang.cindex.Cursor):
        if cursor.spelling not in self.CallFunctions:
            self.CallFunctions.append({
                "Name"  : cursor.spelling,
                "Line"  : cursor.location.line,
                })


    def __str__(self):
        """文字列化
        """

        return f"{self.FunctionName}({','.join([f'{ArgName}:{ArgType}' for ArgName, ArgType in self.Args])})"


def ProcParse(cursor:clang.cindex.Cursor, AnalysisedFunction:FunctionDecl):
    """関数内処理ごとの解析

    Args:
        cursor (clang.cindex.Cursor): 処理へのカーソル
        FunctionName (str): 関数名
    """    

    # 変数定義の判定
    if cursor.kind.name == "VAR_DECL":
        # volatile変数の判定
        if "volatile" in cursor.type.spelling:
            AnalysisedFunction.IncludeVolatile = True

    # 制御文の判定
    if cursor.kind.name == "FOR_STMT":
        AnalysisedFunction.Status["for"] = "○"
    elif cursor.kind.name == "IF_STMT":
        AnalysisedFunction.Status["if"] = "○"
    elif cursor.kind.name == "SWITCH_STMT":
        AnalysisedFunction.Status["switch"] = "○"
    elif cursor.kind.name == "WHILE_STMT":
        AnalysisedFunction.Status["while"] = "○"

    # 関数呼び出しの判定
    if cursor.kind.name == "CALL_EXPR":
        AnalysisedFunction.AddCallFunction(cursor)

    for child in cursor.get_children():
        ProcParse(cursor=child, AnalysisedFunction=AnalysisedFunction)

def ProcCompoundStmt(cursor:clang.cindex.Cursor, AnalysisedFunction:FunctionDecl):
    """関数内処理抽出

    Args:
        cursor (clang.cindex.Cursor): 関数へのカーソル
        FunctionName (str): 関数名
    """    
    for child in cursor.get_children():
        ProcParse(cursor=child, AnalysisedFunction=AnalysisedFunction)

def ProcFunctionDecl(cursor:clang.cindex.Cursor):
    """関数ノード内処理
    ソース内の関数プロトタイプ部分と関数本体部分の2回呼び出される。
    child.kind.name == "COMPOUND_STMT"の時、本体部分になる

    Args:
        cursor (clang.cindex.Cursor): 関数ノードへのカーソル
    """    
    
    AnalysisedFunction = FunctionDecl(FunctionName=cursor.spelling)
    AnalysisedFunction.File = f"{cursor.location.file.name}"
    AnalysisedFunction.Line = f"{cursor.location.line}"

    logger.info(f"analysing {AnalysisedFunction.FunctionName} ...")

    # 子ノードを解析
    isPrototype = True
    for child in cursor.get_children():
        # 引数の解析
        if child.kind.name == "PARM_DECL":
            AnalysisedFunction.AddArg(child)

        # 関数内処理の解析
        elif child.kind.name == "COMPOUND_STMT":
            ProcCompoundStmt(
                cursor=child,
                AnalysisedFunction=AnalysisedFunction)
            isPrototype = False

    if isPrototype == True:
        func_profile, created = Function.objects.get_or_create(
            name = AnalysisedFunction.FunctionName,
            defaults = {
                "return_type" : cursor.result_type.spelling,
                "arguments" : AnalysisedFunction.GetArgs(),
                "file" : AnalysisedFunction.File,
                "line" : AnalysisedFunction.Line,
                "static" : cursor.is_static_method(),
                "const" : cursor.is_const_method(),
                "is_prototype" : isPrototype
            }
        )
    else:
        func_profile, created = Function.objects.update_or_create(
            name = AnalysisedFunction.FunctionName,
            defaults = {
                "return_type" : cursor.result_type.spelling,
                "arguments" : AnalysisedFunction.GetArgs(),
                "file" : AnalysisedFunction.File,
                "line" : AnalysisedFunction.Line,
                "static" : cursor.is_static_method(),
                "const" : cursor.is_const_method(),
                "is_prototype" : isPrototype
            }
        )

    # register function relations
    for func in AnalysisedFunction.CallFunctions:
        profile, created = FunctionRelation.objects.get_or_create(
            call_from = func_profile,
            call_to = Function.objects.get(name=func["Name"]),
            line = func["Line"],
            file = AnalysisedFunction.File,

            defaults = {
                "call_from" : func_profile,
                "call_to"   : Function.objects.get(name=func["Name"]),
                "line"      : func["Line"],
                "file"      : AnalysisedFunction.File,
            }
        )

    # 関数属性(static/extern)記録
    AnalysisedFunction.StorageClass = cursor.storage_class

    # 呼び出し関数の判定
    CallFuncType = [FunctionDeclear[func["Name"]].StorageClass.name for func in AnalysisedFunction.CallFunctions]
    if "EXTERN" in CallFuncType:
        AnalysisedFunction.Status["call_extern"] = "○"
    if "STATIC" in CallFuncType:
        AnalysisedFunction.Status["call_static"] = "○"

    # 関数戻り値判定
    AnalysisedFunction.SetReturnType(cursor)
    ReturnType = AnalysisedFunction.GetReturnType()
    if ReturnType["CanonicalType"] == "void":
        AnalysisedFunction.Status["戻り値"] = "void型"
    elif "*" in ReturnType["CanonicalType"]:
        AnalysisedFunction.Status["戻り値"] = "ポインタ型"
    else:
        AnalysisedFunction.Status["戻り値"] = "データ型"

    # 引数判定
    for arg in AnalysisedFunction.GetArgs():
        if arg["Kind"] == "POINTER":
            if "void" in arg["CanonicalType"]:
                AnalysisedFunction.Status["引数"] = "voidポインタ型含"
            else:
                AnalysisedFunction.Status["引数"] = "ポインタ型含"
        else:
            if "void" in arg["CanonicalType"]:
                AnalysisedFunction.Status["引数"] = "void型"
            else:
                AnalysisedFunction.Status["引数"] = "データ型"

    # その他判定
    if AnalysisedFunction.IncludeVolatile == True:
        AnalysisedFunction.Status["other"] = "volatile変数あり"

    elif "○" in [
            AnalysisedFunction.Status["for"],
            AnalysisedFunction.Status["if"],
            AnalysisedFunction.Status["switch"],
            AnalysisedFunction.Status["while"]]:
        
        AnalysisedFunction.Status["other"] = "－"

    else:
        AnalysisedFunction.Status["other"] = "データセット処理のみ"


    # 関数定義登録
    if AnalysisedFunction.FunctionName not in FunctionDeclear:
        FunctionDeclear[AnalysisedFunction.FunctionName] = AnalysisedFunction
    else:
        AnalysedFunctionList.append(AnalysisedFunction)

#    pprint.pprint(AnalysisedFunction.Status)
        
def dump_node(cursor:clang.cindex.Cursor):
    """ファイル全体を解析する

    Args:
        cursor (clang.cindex.Cursor): カーソル
    """

    # 関数ノード取得
    for child in cursor.get_children():
        if child.kind.name == "FUNCTION_DECL":
            ProcFunctionDecl(child)

        pass

def Survey__(TargetSourceFile:str, ClangArgs:str):
    """ファイル調査
    対象ファイルを解析する。
    ASTを作成し、関数ノードを取得する。

    Args:
        TargetSourceFile (str): 対象ファイル
    """    
    index = clang.cindex.Index.create()
    translation_unit = index.parse(TargetSourceFile, args=shlex.split(ClangArgs))
    dump_node(translation_unit.cursor)

def WriteCsv(FileName:str):
    """CSV書き出し
    調査結果をCSVに書き出す。

    Args:
        FileName (str): 出力ファイル名
    """    
    FileExist = pathlib.Path(FileName).exists()

    with open (FileName, "a") as f:
        writer = csv.writer(f)

        # 新規作成時のみヘッダ追加
        if FileExist == False:
            # ヘッダ部分
            writer.writerow([
                "ファイル",
                "行番号",
                "戻り値型",
                "関数名",
                "戻り値種別",
                "引数",
                "for",
                "if",
                "switch",
                "while",
                "extern",
                "static",
                "その他"
            ])
        
        # データ部分
        for item in AnalysedFunctionList:
            # 戻り値表示整形
            RetType = item.ReturnType["Type"]
            if item.ReturnType["Type"] != item.ReturnType["CanonicalType"]:
                RetType = f"{item.ReturnType['Type']}({item.ReturnType['CanonicalType']})"

            writer.writerow([
                item.File,                  # 定義ファイル名
                item.Line,                  # 定義行番号
                RetType,                    # 戻り値 
                item.FunctionName,          # 関数名
                item.Status["戻り値"],      # 戻り値種別 
                item.Status["引数"],        # 引数
                item.Status["for"],
                item.Status["if"],
                item.Status["switch"],
                item.Status["while"],
                item.Status["call_extern"],
                item.Status["call_static"],
                item.Status["other"]
            ])


class Command__(BaseCommand):
    help = "関数調査"

    def handle(self, *args, **options):
        try:
            logger.info("Function Survey Start")
            logger.info(f" target file: {options['target-file']}")
            logger.info(f" clang args : {options['clang_args']}")
            
            Survey(
                TargetSourceFile = options["target-file"],
                ClangArgs = options["clang_args"])
#            WriteCsv("all.csv")
            
        except Exception as e:
            logger.error(f"exception {e}", exc_info=True)
            pass

    def add_arguments(self, parser):
        parser.add_argument('--clang-args', nargs='?', default='target', type=str)
        parser.add_argument('target-file', nargs='?', default='', type=str)


class Command(BaseCommand):
    help = "関数調査"

    def handle(self, *args, **options):
        try:
            logger.info("Function Survey Start")
            logger.info(f" target file: {options['target-file']}")
            logger.info(f" clang args : {options['clang_args']}")
            
            survey = Survey(
                TargetSourceFile = options["target-file"],
                ClangArgs = options["clang_args"]
            )
            ret = survey.Survey()
            logger.info(f" {len(ret)} function(s)")


            
        except Exception as e:
            logger.error(f"exception {e}", exc_info=True)


        finally:
            pass

    def add_arguments(self, parser):
        parser.add_argument('--clang-args', nargs='?', default='target', type=str)
        parser.add_argument('target-file', nargs='?', default='', type=str)
