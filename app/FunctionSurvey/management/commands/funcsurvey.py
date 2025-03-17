from django.db import transaction
from django.core.management.base import BaseCommand
from ...models import Project, Function, FunctionRelation
from ...survey import Survey

import logging
import datetime
from pathlib import Path

logger = logging.getLogger('Survey')

class Command(BaseCommand):
    """funcsurvey command class

    Args:
        BaseCommand (_type_): Django base command class
    """    
    help = "関数調査"
    _Project = None
    _Functions = {}
    _Variables = []

    def _write_db(self):
        """write project to database

        """        
        # write project table
        project_profile, created = Project.objects.get_or_create(
            name = self._Project,
            defaults = {}
        )

        # select write functions
        # fillter non-prototype functions
        write_func = []
        for func in self._Functions:
            # target function
            if self._Functions[func]["IsPrototype"] == False:

                # add call functions from target function
                for call_to_func in self._Functions[func]["CallFunctions"]:
                    # skip non-registed function
                    if call_to_func["Name"] not in self._Functions.keys():
                        logger.warning(f"  skip {func} -> {call_to_func['Name']}")    
                        continue

                    if call_to_func["Name"] not in write_func:
                        write_func.append(call_to_func["Name"])
                
                # add target function
                if func not in write_func:
                    # skip non-registed function
                    if func not in self._Functions.keys():
                        logger.warning(f"  skip {func}")    
                        continue

                    write_func.append(func)

        # atomic session
        with transaction.atomic():
            # write & get record from function table
            func_profile = {}
            for func in write_func:
                # set value
                value = {
                    "project"       : project_profile,
                    "return_type"   : self._Functions[func]["ReturnType"],
                    "arguments"     : self._Functions[func]["Args"],
                    "file"          : self._Functions[func]["File"],
                    "line"          : self._Functions[func]["Line"],
                    "end_line"      : self._Functions[func]["EndLine"],
                    "static"        : self._Functions[func]["IsStatic"],
                    "const"         : self._Functions[func]["IsConst"],
                    "is_prototype"  : self._Functions[func]["IsPrototype"]
                }

                # The written function is NOT a prototype. In this case, it update or create record.
                if self._Functions[func]["IsPrototype"] == False:
                    # update or get record profile
                    func_profile[func], created = Function.objects.update_or_create(
                        project = project_profile,
                        name = func,
                        defaults = value
                    )

                # The written function is a prototype. In this case, it create record.
                else:
                    # append and get record profile
                    func_profile[func], created = Function.objects.get_or_create(
                        project = project_profile,
                        name = func,
                        defaults = value
                    )

            # write function relation table
            for base_func in write_func:
                # scan call other funcsion from base function
                for call_to_func in self._Functions[base_func]["CallFunctions"]:
                    if call_to_func["Name"] not in func_profile.keys():
                        logger.warning(f"  skip {base_func} -> {call_to_func['Name']}")    
                        continue

                    # add function relation
                    #  - due to db textfield compare unexpected , file name isn't include compare keywords
                    call_func_profile, created = FunctionRelation.objects.get_or_create(
                        project = project_profile,
                        call_from = func_profile[base_func],
                        call_to = func_profile[call_to_func["Name"]],
                        line = call_to_func["Line"],
                        defaults = {
                            "project"   : project_profile,
                            "call_from" : func_profile[base_func],
                            "call_to"   : func_profile[call_to_func["Name"]],
                            "line"      : call_to_func["Line"],
                            "file"      : self._Functions[base_func]["File"],
                        }
                    )

        logger.info(f" {len(write_func)} function(s)")


        pass        

    def handle(self, *args, **options):
        """command entry point

        """        
        
        try:
            start_time = datetime.datetime.now()

            verbosity = options.get('verbosity', 1)
            if verbosity >= 2:
                logger.setLevel(logging.DEBUG)

            logger.info("Function Survey Start")
            logger.info(f" {start_time.strftime('%Y/%m/%d %H:%M:%S')}")
            logger.info(f" Project    : {options['project']}")
            logger.info(f" target file: {options['target-file']}")
            logger.info(f" clang args : {options['clang_args']}")
            
            self._Project = options['project']

            # survey target file
            survey = Survey(
                TargetSourceFile = options["target-file"],
                ClangArgs = options["clang_args"]
            )
            analysised = survey.Survey()
            self._Functions = analysised["Functions"]
            self._Variables = analysised["Variables"]

            # adjust self._Functions
            remove_path_prefix = Path(options["remove_path_prefix"])
            for func in self._Functions:
                # adjust file path
                filepath = Path(self._Functions[func]["File"])

                # When the path prefix matches exactly
                if filepath.is_relative_to(remove_path_prefix):
                    self._Functions[func]["File"] = str(filepath.relative_to(remove_path_prefix))

                # When the path prefix is included in the path
                else:
                    rm_prefix = remove_path_prefix.parent

                    while str(rm_prefix) != ".":
                        if filepath.is_relative_to(rm_prefix):
                            self._Functions[func]["File"] = filepath.relative_to(rm_prefix)
                            break

                        rm_prefix = rm_prefix.parent


            # write db
            self._write_db()
            pass


            
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
        parser.add_argument('--clang-args', nargs='?', default='target', type=str)
        parser.add_argument('--remove-path-prefix', nargs='?', default="target", type=str)
        parser.add_argument('target-file', nargs='?', default='', type=str)
