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

    def _TraceFunctionTree(self, FunctionName:str="", Depth:int=1):
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

            # get upper functions
            upper_functions = self._ProjectFunctionRelation.filter(call_to__name = FunctionName).values_list("call_from__name", flat=True).distinct()
            for func_name in list(upper_functions):
                NextElement = self._TraceFunctionTree(FunctionName = func_name, Depth=Depth - 1)
                TreeElement["next"].append(NextElement)
        

        else:
            # search lower functions
            TreeElement = {
                "name"  : FunctionName,
                "next": [],
            }

            # get lower functions
            lower_functions = self._ProjectFunctionRelation.filter(call_from__name = FunctionName).values_list("call_to__name", flat=True).distinct()
            for func_name in list(lower_functions):
                NextElement = self._TraceFunctionTree(FunctionName = func_name, Depth=Depth + 1)
                TreeElement["next"].append(NextElement)
 


        return TreeElement
        
    def _DisplayFunctionTree(self, FunctionTree:dict, depth = 0):

        DisplayFunction = self._ProjectFunction.filter(name = FunctionTree['name']).first()
        logger.info(f"{"\t" * depth} {"static " if DisplayFunction.static else ""}{DisplayFunction.return_type} {DisplayFunction.name}")

        for func in FunctionTree["next"]:
            self._DisplayFunctionTree(FunctionTree = func, depth = depth + 1)
        pass


    def handle(self, *args, **options):
        """command entry point

        """        
        try:
            start_time = datetime.datetime.now()


            # display start up infomation
            logger.info("Function Tree Start")
            logger.info(f" {start_time.strftime('%Y/%m/%d %H:%M:%S')}")
            logger.info(f"Target project : {options['project']}")
            logger.info(f"Target function : {options['target-function']}")
            
            # select project data
            self._ProjectFunction = Function.objects.filter(project__name=options["project"])
            self._ProjectFunctionRelation = FunctionRelation.objects.filter(project__name=options["project"])

            # trace function tree
            self._FunctionTree["upper"] = self._TraceFunctionTree(FunctionName = options["target-function"], Depth = options["upper"])
            self._FunctionTree["lower"] = self._TraceFunctionTree(FunctionName = options["target-function"], Depth = -options["lower"])
            
            # display function tree
            if len(self._FunctionTree["upper"]["next"]) > 0:
                logger.info("** Upper Function Tree")
                self._DisplayFunctionTree(FunctionTree = self._FunctionTree["upper"])

            if len(self._FunctionTree["lower"]["next"]) > 0:
                logger.info("** Lower Function Tree")
                self._DisplayFunctionTree(FunctionTree = self._FunctionTree["lower"])

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
