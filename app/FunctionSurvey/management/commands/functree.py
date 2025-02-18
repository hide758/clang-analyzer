from django.core.management.base import BaseCommand
from ...models import Project, Function, FunctionRelation

import logging
import datetime

logger = logging.getLogger('Survey')


class Command(BaseCommand):
    """functree command class

    Args:
        BaseCommand (_type_): Django base command class
    """    

    help = "function tree"
    _ProjectFunction = None
    _ProjectFunctionRelation = None
    _FunctionTree = {
        "upper" : [],
        "lower" : []
    }

    def _TraceUpperTree(self, FunctionName:str="", Depth:int=1):
        """trace function tree (upper)

        Args:
            FunctionName (_type_): target function
            Depth (_type_): trace level
        """        

        if Depth == 0:
            return {
                "name"  : FunctionName,
                "next": [],
            }
        
        elif Depth > 0:
            # search upper functions
            TreeElement = {
                "name"  : FunctionName,
                "next": [],
            }

            upper_functions = self._ProjectFunctionRelation.filter(call_to__name = FunctionName).values_list("call_from__name", flat=True).distinct()
            for func_name in list(upper_functions):
                NextElement = self._TraceUpperTree(FunctionName = func_name, Depth=Depth - 1)
                TreeElement["next"].append(NextElement)
        

        else:
            # search lower functions
            TreeElement = {
                "name"  : FunctionName,
                "next": [],
            }

            lower_functions = self._ProjectFunctionRelation.filter(call_from__name = FunctionName).values_list("call_to__name", flat=True).distinct()
            for func_name in list(lower_functions):
                NextElement = self._TraceUpperTree(FunctionName = func_name, Depth=Depth + 1)
                TreeElement["next"].append(NextElement)
 


        return TreeElement
        


    def handle(self, *args, **options):
        """command entry point

        """        
        try:
            start_time = datetime.datetime.now()


            logger.info("Function Tree Start")
            logger.info(f" {start_time.strftime('%Y/%m/%d %H:%M:%S')}")
            
            # select project data
            self._ProjectFunction = Function.objects.filter(project__name=options["project"])
            self._ProjectFunctionRelation = FunctionRelation.objects.filter(project__name=options["project"])

            # trace function tree
            self._FunctionTree["upper"] = self._TraceUpperTree(FunctionName = options["target-function"], Depth = options["upper"])
            self._FunctionTree["lower"] = self._TraceUpperTree(FunctionName = options["target-function"], Depth = -options["lower"])
            pass

            
        except Exception as e:
            logger.error(f"exception {e}", exc_info=True)


        finally:
            logger.debug(f" elapsed time {(datetime.datetime.now() - start_time).total_seconds()}")


    def add_arguments(self, parser):
        """regist command arguments

        Args:
            parser (_type_): argument parser
        """        

        parser.add_argument('--project', nargs='?', default=None, type=str)
        parser.add_argument('--upper', nargs='?', default=1, type=int)
        parser.add_argument('--lower', nargs='?', default=1, type=int)
        parser.add_argument('target-function', nargs='?', default='', type=str)
