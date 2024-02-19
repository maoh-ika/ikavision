import os
import subprocess

BACKUP_TOOL_PATH = '/Users/maohika/work/dynamodb-copy-table/dynamodb-copy-table.py'
ENV = 'dev'

os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'

def _backup(table_name):
    command = ['python3', BACKUP_TOOL_PATH, f'{table_name}-{ENV}', f'{table_name}-{ENV}-backup']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print("標準出力:", stdout.decode())
    print("標準エラー出力:", stderr.decode())


# battle-analysis-job
_backup('battle-analysis-job')

# battle-analysis-result
_backup('battle-analysis-result')

# battle-environment
_backup('battle-environment')

# battle-statistics
_backup('battle-statistics')

del os.environ['AWS_DEFAULT_REGION']