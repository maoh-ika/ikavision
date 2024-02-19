import os
import subprocess

BACKUP_TOOL_PATH = '/Users/maohika/work/dynamodb-copy-table/dynamodb-copy-table.py'
ENV = 'dev'

os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'
os.environ['DISABLE_CREATION'] = 'yes'

def _restore(table_name):
    command = ['python3', BACKUP_TOOL_PATH, f'{table_name}-{ENV}-backup', f'{table_name}-{ENV}']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print("標準出力:", stdout.decode())
    print("標準エラー出力:", stderr.decode())


# battle-analysis-job
_restore('battle-analysis-job')

# battle-analysis-result
_restore('battle-analysis-result')

# battle-environment
_restore('battle-environment')

# battle-statistics
_restore('battle-statistics')

del os.environ['AWS_DEFAULT_REGION']
del os.environ['DISABLE_CREATION']