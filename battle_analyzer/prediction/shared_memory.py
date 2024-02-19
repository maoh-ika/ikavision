from multiprocessing import shared_memory
import pickle
import numpy as np

class SharedMemory:
    SHM_NAME = 'shared_memory'
    SHM_SIZE = 1024 * 1024 * 1024
    SHM_ID = 0
    SHM_BUF = None

    @classmethod
    def set_id(cls, shm_id: int):
        cls.SHM_ID = shm_id

    @classmethod
    def unique_shm_name(cls) -> str:
        return f'{cls.SHM_NAME}_{cls.SHM_ID}'

    @classmethod
    def create(cls):
       cls.SHM_BUF = shared_memory.SharedMemory(create=True, size=cls.SHM_SIZE, name=cls.unique_shm_name())
    
    @classmethod
    def clear(cls): 
        shared_memory.SharedMemory(name=cls.unique_shm_name()).unlink()
        cls.SHM_BUF = None
    
    @classmethod
    def reset(cls):
        try:
            cls.clear()
        except:
            pass
        cls.create()
    
    @classmethod
    def write(cls, data: any):
        serialized = cls.serialize(data)
        arr = np.array([serialized])
        shm = shared_memory.SharedMemory(name=cls.unique_shm_name())
        narr = np.ndarray((1,), dtype=f'S{cls.SHM_SIZE}', buffer=shm.buf)
        narr[:] = arr[:]

    @classmethod
    def read(cls):
        shm = shared_memory.SharedMemory(name=cls.unique_shm_name())
        narr = np.ndarray((1,), dtype=f'S{cls.SHM_SIZE}', buffer=shm.buf)
        b = bytes(narr)
        obj_size = int.from_bytes(b[:4], 'big')
        obj = pickle.loads(b[4:obj_size + 4]) if obj_size > 0 else None
        return obj

    @classmethod
    def serialize(cls, data) -> bytes:
        """
        Serialize ikalamps to fixed size bytes.
        [total_size(4bytes)][total_items(4bytes)][pkl_size(4bytes)][pkl_data]...[padding]
        """

        b = pickle.dumps(data)
        obj_size = len(b).to_bytes(4, 'big')
        b = obj_size + b
        if len(b) > cls.SHM_SIZE:
            raise Exception(f'size of serialized data exceeds max memory size: {len(b)}')
        b = b.ljust(cls.SHM_SIZE, b'0')
        return b