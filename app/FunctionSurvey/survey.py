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
        """関数呼び出し追加

        Args:
            cursor (clang.cindex.Cursor): 関数呼び出し要素カーソル
        """        
        if cursor.spelling not in self.CallFunctions:
            self.CallFunctions.append({
                "Name"  : cursor.spelling,
                "Line"  : cursor.location.line,
                })


    def __str__(self):
        """文字列化
        """

        return f"{self.Name}({','.join([f'{ArgName}:{ArgType}' for ArgName, ArgType in self.Args])})"



class VarDecl:
    """変数解析クラス
    """    
    def __init__(self, cursor:clang.cindex.Cursor, Scope:str = None):
        """初期化

        Args:
            cursor (clang.cindex.Cursor): 要素カーソル
        """        
        self.Scope = Scope
        self.Type = self._get_type_name(cursor.type)
        self.Name = cursor.spelling
        self.File = cursor.location.file.name
        self.Line = cursor.location.line

        self.IsArray = "ARRAY" in cursor.type.kind.name
        self.ArraySize = cursor.type.get_array_size()

        self.IsPointer = cursor.type.kind.name  == "POINTER"
        self.IsExtern = cursor.storage_class.name == "EXTERN"
        self.IsStatic = cursor.storage_class.name == "STATIC"
        self.IsArgument = cursor.kind.name == "PARM_DECL"

        self.IsConst = cursor.type.get_canonical().is_const_qualified()

        pass


    def _get_type_name(self, cursor:clang.cindex.Cursor):
        """
        return variable type name
        """

        # resolve type name recursively
        if cursor.kind.name in ("CONSTANTARRAY",
                            "INCOMPLETEARRAY",
                            "VARIABLEARRAY"):
            return self._get_type_name(cursor.get_array_element_type())


        # remove "const"
        if "const " in cursor.spelling:
            return cursor.spelling.replace("const ", "")
        else:
            return cursor.spelling


    def __str__(self):
        """文字列化
        """

        return f"{self.Name}({','.join([f'{ArgName}:{ArgType}' for ArgName, ArgType in self.Args])})"


class Survey():
    help = "survey source file"

    def __init__(self, TargetSourceFile:str="", ClangArgs:str=""):
        """initialize

        Args:
            TargetSourceFile (str, optional): Analyzing target file (Defaults to "").
            ClangArgs (str, optional): command-line option to clang (Defaults to "").
        """        
        self._TargetSourceFile = TargetSourceFile
        self._ClangArgs = ClangArgs
        self._Functions = {}
        self._Variables = []

    def Survey(self) -> dict:
        """function survey
        analyze each function in the source file.
        make AST and dump it.

        """

        index = clang.cindex.Index.create()
        translation_unit = index.parse(self._TargetSourceFile, args=shlex.split(self._ClangArgs))
        self._dump_node(translation_unit.cursor)

        return {
            "Functions"  :self._Functions,
            "Variables"  :self._Variables,
        }

    def _dump_node(self, cursor:clang.cindex.Cursor):
        """ファイル全体を解析する

        Args:
            cursor (clang.cindex.Cursor): カーソル
        """

        # 関数ノード取得
        for child in cursor.get_children():
#            if child.location.file.name != self._TargetSourceFile:
#                continue

            # declear function
            if child.kind.name == "FUNCTION_DECL":
                self._ProcFunctionDecl(child)

            elif child.kind.name == "VAR_DECL":
                self._Variables.append(vars(VarDecl(cursor=child, Scope = None)))


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
                self._Variables.append(vars(VarDecl(cursor=child, Scope = AnalysisedFunction.Name)))

            # 関数内処理の解析
            elif child.kind.name == "COMPOUND_STMT":
                self._ProcCompoundStmt(
                    cursor=child,
                    AnalysisedFunction=AnalysisedFunction)
                AnalysisedFunction.IsPrototype = False

#            else:
#                break
                

        # 関数定義登録
        self._Functions[AnalysisedFunction.Name] = vars(AnalysisedFunction)


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

        # analyze variable declaration
        elif cursor.kind.name == "VAR_DECL":
            self._Variables.append(vars(VarDecl(cursor=cursor, Scope = AnalysisedFunction.Name)))

        for child in cursor.get_children():
            self._ProcParse(cursor=child, AnalysisedFunction=AnalysisedFunction)

if __name__ == "__main__":
    survey = Survey(
        TargetSourceFile="target/usv/prm/paxcmp.c",
        ClangArgs="-I target/ansi -I target/usv/inc -D SPINDLE"
    )
    ret = survey.Survey()
    pass
