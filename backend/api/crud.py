from sqlalchemy.orm import Session
from api.models import EOLLevel1Master# ✅ changed here

def get_all_data(db: Session, limit: int = 100):
    records = db.query(EOLLevel1Master).limit(limit).all()
    result = []
    for r in records:
        result.append({
            "RECORD_ID": r.RECORD_ID,
            "ENGINE_NO": r.ENGINE_NO,
            "VC_NO": r.VC_NO,
            "VIN_NO": r.VIN_NO,
            "ECU_TYPE": r.ECU_TYPE,
            "TIME_TOFLASH": r.TIME_TOFLASH,
            "FLASHING_REMARK": r.FLASHING_REMARK,
            "WRITING_REMARK": r.WRITING_REMARK,
            "PAIRING_REMARK": r.PAIRING_REMARK,
            "STATIC_REMARK": r.STATIC_REMARK,
            "FLASHING_STATUS": r.FLASHING_STATUS,
            "WRITING_STATUS": r.WRITING_STATUS,
            "PAIRING_STATUS": r.PAIRING_STATUS,
            "STATIC_STATUS": r.STATIC_STATUS,
            "DTC_CODE": r.DTC_CODE,
            "STATION_ID": r.STATION_ID,
            "TCF_LINE": r.TCF_LINE,
            "PLANT_CODE": r.PLANT_CODE,
            "PROD_DATETIME": r.PROD_DATETIME,
            "TOOL_VERSION": r.TOOL_VERSION,
            "CYCLE_TIME": r.CYCLE_TIME,
            "IS_TRIAL": r.IS_TRIAL,
            "FMID": r.FMID,
            "BID": r.BID,
            "BL_NO": r.BL_NO,
            "BL_VER": r.BL_VER,
            "DTS_TRANSFER_DATE": r.DTS_TRANSFER_DATE
        })
    return result
def get_by_date_range(db: Session, start_date: str, end_date: str):
    return db.query(EOLLevel1Master).filter(
        EOLLevel1Master.PROD_DATETIME.between(start_date, end_date)
    ).all()

def get_by_plant(db: Session, plant_code: str):
    return db.query(EOLLevel1Master).filter(
        EOLLevel1Master.PLANT_CODE == plant_code
    ).all()
