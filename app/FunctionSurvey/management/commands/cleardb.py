from django.core.management.base import BaseCommand
from ...models import Project, Function, FunctionRelation, Variable

import logging
import datetime

logger = logging.getLogger('Survey')


class Command(BaseCommand):
    """exportdb command class

    Args:
        BaseCommand (_type_): Django base command class
    """    

    help = "DBクリア"

    def handle(self, *args, **options):
        """command entry point

        """        
        try:
            start_time = datetime.datetime.now()

            delete_table = [FunctionRelation, Variable, Function, Project]

            logger.info("Database Clear Start")
            logger.info(f" {start_time.strftime('%Y/%m/%d %H:%M:%S')}")

            # delete all records
            for table in delete_table:
                table.objects.all().delete()


            
        except Exception as e:
            logger.error(f"exception {e}", exc_info=True)


        finally:
            logger.debug(f" elapsed time {(datetime.datetime.now() - start_time).total_seconds()}")

