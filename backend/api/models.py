from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from .db import Base


class EOLLevel1Master(Base):
    __tablename__ = "EOL_LEVEL1_MASTER"

    RECORD_ID = Column(BigInteger, primary_key=True, index=True)
    ENGINE_NO = Column(String(50))
    VC_NO = Column(String(20))
    VIN_NO = Column(String(20))
    ECU_TYPE = Column(String(100))
    TIME_TOFLASH = Column(Integer)
    FLASHING_REMARK = Column(String(1000))
    WRITING_REMARK = Column(String(1000))
    PAIRING_REMARK = Column(String(1000))
    STATIC_REMARK = Column(String(1000))
    FLASHING_STATUS = Column(Integer)
    WRITING_STATUS = Column(Integer)
    PAIRING_STATUS = Column(Integer)
    STATIC_STATUS = Column(Integer)
    DTC_CODE = Column(String(1000))
    STATION_ID = Column(String(50))
    TCF_LINE = Column(String(50))
    PLANT_CODE = Column(String(5))
    PROD_DATETIME = Column(DateTime)
    TOOL_VERSION = Column(String(100))
    CYCLE_TIME = Column(String(100))
    IS_TRIAL = Column(Integer)
    FMID = Column(BigInteger)
    BID = Column(BigInteger)
    BL_NO = Column(String(50))
    BL_VER = Column(String(50))
    DTS_TRANSFER_DATE = Column(DateTime)



