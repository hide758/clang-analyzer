import logging
import shlex
import clang.cindex

logger = logging.getLogger('Survey')


class FunctionDecl:
    """関数解析クラス
    """    
    def __init__(self, FunctionName:str):
        """初期化

        Args:
            FunctionName (str): 関数名
        """        
        self.Name = FunctionName
        self.IsPrototype = True
        self.IsStatic = False
        self.IsConst = False
        self.Args = []
        self.ReturnType = {}
        self.CallFunctions = []


    def AddArg(self, cursor:clang.cindex.Cursor):
        """関数引数追加

        Args:
            cursor (clang.cindex.Cursor): 要素カーソル
        """        
        self.Args.append({
            "Type"  : cursor.type.spelling,
            "CanonicalType"  : cursor.type.get_canonical().spelling,
            "IsPointer"  : cursor.type.kind.name  == "POINTER",
            "IsConst"   : cursor.type.is_const_qualified(),
            "Name"  : cursor.spelling
        })

    def GetArgs(self) -> list:
        """関数引数取得

        Returns:
            list: 引数リスト
        """        
        return self.Args

    def AddCallFunction(self, cursor:clang.cindex.Cursor):
        if cursor.spelling not in self.CallFunctions:
            self.CallFunctions.append({
                "Name"  : cursor.spelling,
                "Line"  : cursor.location.line,
                })


    def __str__(self):
        """文字列化
        """

        return f"{self.Name}({','.join([f'{ArgName}:{ArgType}' for ArgName, ArgType in self.Args])})"




class Survey():
    help = "survey source file"

    def __init__(self, TargetSourceFile:str="", ClangArgs:str=""):
        self._TargetSourceFile = TargetSourceFile
        self._ClangArgs = ClangArgs
        self._Functions = {}

    def Survey(self) -> dict:
        """function survey
        analyze each function in the source file.
        make AST and dump it.

        """

        index = clang.cindex.Index.create()
        translation_unit = index.parse(self._TargetSourceFile, args=shlex.split(self._ClangArgs))
        self._dump_node(translation_unit.cursor)

        return self._Functions

    def _dump_node(self, cursor:clang.cindex.Cursor):
        """ファイル全体を解析する

        Args:
            cursor (clang.cindex.Cursor): カーソル
        """

        # 関数ノード取得
        for child in cursor.get_children():
            # declear function
            if child.kind.name == "FUNCTION_DECL":
                self._ProcFunctionDecl(child)


    def _ProcFunctionDecl(self, cursor:clang.cindex.Cursor):
        """関数ノード内処理
        ソース内の関数プロトタイプ部分と関数本体部分の2回呼び出される。
        child.kind.name == "COMPOUND_STMT"の時、本体部分になる

        Args:
            cursor (clang.cindex.Cursor): 関数ノードへのカーソル
        """    
        
        AnalysisedFunction = FunctionDecl(FunctionName=cursor.spelling)
        AnalysisedFunction.File = f"{cursor.location.file.name}"
        AnalysisedFunction.Line = f"{cursor.location.line}"
        AnalysisedFunction.IsPrototype = True
        AnalysisedFunction.IsStatic = cursor.storage_class.name=="STATIC"
        AnalysisedFunction.IsConst = cursor.is_const_method()
        AnalysisedFunction.ReturnType = cursor.type.get_result().spelling
        

        logger.debug(f"analysing {AnalysisedFunction.Name} ...")

        # 子ノードを解析
        for child in cursor.get_children():
            # 引数の解析
            if child.kind.name == "PARM_DECL":
                AnalysisedFunction.AddArg(child)

            # 関数内処理の解析
            elif child.kind.name == "COMPOUND_STMT":
                self._ProcCompoundStmt(
                    cursor=child,
                    AnalysisedFunction=AnalysisedFunction)
                AnalysisedFunction.IsPrototype = False

            else:
                break
                

        # 関数定義登録
        self._Functions[AnalysisedFunction.Name] = AnalysisedFunction


    def _ProcCompoundStmt(self, cursor:clang.cindex.Cursor, AnalysisedFunction:FunctionDecl):
        """関数内処理抽出

        Args:
            cursor (clang.cindex.Cursor): 関数へのカーソル
            FunctionName (str): 関数名
        """    
        for child in cursor.get_children():
            self._ProcParse(cursor=child, AnalysisedFunction=AnalysisedFunction)

    def _ProcParse(self, cursor:clang.cindex.Cursor, AnalysisedFunction:FunctionDecl):
        """関数内処理ごとの解析

        Args:
            cursor (clang.cindex.Cursor): 処理へのカーソル
            FunctionName (str): 関数名
        """    

        # 関数呼び出しの判定
        if cursor.kind.name == "CALL_EXPR":
            AnalysisedFunction.AddCallFunction(cursor)

        for child in cursor.get_children():
            self._ProcParse(cursor=child, AnalysisedFunction=AnalysisedFunction)

if __name__ == "__main__":
    survey = Survey(
        TargetSourceFile="target/usv/srv/valm.c",
        ClangArgs="-I target/ansi -I target/usv/inc -D SPINDLE"
    )
    ret = survey.Survey()
    pass
