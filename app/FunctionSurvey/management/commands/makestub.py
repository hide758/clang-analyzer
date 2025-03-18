from django.core.management.base import BaseCommand
from ...models import Project, Function, FunctionRelation

import logging
import datetime
from pathlib import Path

logger = logging.getLogger('Survey')

class MakeStubFunctions():
    _template_stubfunction="""
/* Stub Function  */
/* file: {BASE_FILE_FULLPATH}:{BASE_LINE} */
/* WINAMS_STUB[{BASE_FILE}:{BASE_FUNCTION_NAME}:AMSTB_{BASE_FUNCTION_NAME}:inout:::] */
/*    {BASE_FUNCTION_NAME} => Stub */
{FUNCTION_PROTOTYPE}
{{
{CONTENT}
}}

"""

    def __init__(self):
        self.Functions = []
        self.CallFunctions = []

    def GetFunctions(self, ProjectName:str=None, FunctionName:list=[]) -> list:
        # return the list of functions which are called another function.
        # This list is sorted by file and location.

        if len(FunctionName) == 0:
            return sorted(list(set([
                rel.call_to for rel in 
                    FunctionRelation.objects.filter(project__name=ProjectName).select_related('call_to')])),
                    key=lambda f: (f.file, f.line))

        else:
            return sorted(list(set([
                rel.call_to for rel in 
                    FunctionRelation.objects.filter(project__name=ProjectName, call_from__name__in=FunctionName).select_related('call_to')])),
                    key=lambda f: (f.file, f.line))

    def GetExternString(self, ExportFunctions:list=None):
        # write the extern declaration of the functions which are called by the functions in ExportFunctions.

        externs = []
        for func in ExportFunctions:
            if func.is_prototype:
                continue

            proto = f"extern {func.return_type} {func.name}({', '.join([f["Declear"] for f in func.arguments])});"
            externs.append(
                proto.replace(f" {func.name}(", f" AMSTB_{func.name}(")
            )
            pass

        return externs

    def GetFunctionBody(self, ExportFunctions:list=None):
        # write the stub function body of the functions in
        # ExportFunctions.

        bodies = []
        for func in ExportFunctions:
            if func.is_prototype:
                continue

            # get the filename from the fullpath
            filename = Path(func.file).name

            # set CONTENT
            if func.return_type == "void":
                content = "\treturn;"
            else:
                content  = f"\tstatic {func.return_type} ret;\n\n"
                content += f"\treturn ret;"
            
            # write the stub function body
            body = self._template_stubfunction.format(
                BASE_FILE_FULLPATH  = func.file,
                BASE_FILE           = filename,
                BASE_LINE           = str(func.line),
                BASE_FUNCTION_NAME  = func.name,
                FUNCTION_PROTOTYPE  = f"{func.return_type} AMSTB_{func.name}({', '.join([f["Declear"] for f in func.arguments])})",
                CONTENT             = content
            )
            bodies.append(body)
            

        return bodies

class Command(BaseCommand):
    """makestub command class

    Args:
        BaseCommand (_type_): Django base command class
    """    

    help = "Make the file contain stub functions"

    def handle(self, *args, **options):
        """command entry point

        """        
        try:
            start_time = datetime.datetime.now()

            logger.info("Make stub file Start")
            logger.info(f" {start_time.strftime('%Y/%m/%d %H:%M:%S')}")

            stub = MakeStubFunctions()

            if options["parent_func"] == "":
                funcs = stub.GetFunctions(ProjectName=options["project"])

            else:
                funcs = stub.GetFunctions(
                    ProjectName=options["project"],
                    FunctionName=options["parent_func"].split(","))

            externs = stub.GetExternString(funcs)
            bodies = stub.GetFunctionBody(funcs)


            # read export template
            with open("template-stub.h", "r") as f:
                stub_h = f.read()

            with open("template-stub.c", "r") as f:
                stub_c = f.read()

            # expand the template
            stub_h = stub_h.format(
                content ="\n".join(externs)
            )
            stub_c = stub_c.format(
                content ="\n".join(bodies)
            )

            with open(options["save_as"] + ".h", "w") as f:
                f.write(stub_h)

            with open(options["save_as"] + ".c", "w") as f:
                f.write(stub_c)


            
        except Exception as e:
            logger.error(f"exception {e}", exc_info=True)


        finally:
            logger.info(f" elapsed time {(datetime.datetime.now() - start_time).total_seconds()}")

    def add_arguments(self, parser):
        """regist command arguments

        Args:
            parser (_type_): argument parser
        """        

        parser.add_argument('--project', nargs='?', default=None, type=str)
        parser.add_argument('--save-as', nargs='?', default="stub", type=str)
        parser.add_argument('--parent-func', nargs='?', default="", type=str)
