import os, logging, sqlite3, glob
import xml.etree.ElementTree as et
from model.tumorItem import HeaderInfo, TumorItem
from model.mapping import fieldMapping, columnMapping
from utility import Utility

class xmlLoadHandler:

    def __init__(self):  
        self._data_dir = os.getcwd() + "\data"
        self._processed_dir = os.getcwd() + "\data\processed"
        self._tumors = []
        self._fieldmapping = fieldMapping
        self._columnmapping = columnMapping

    # process all naaccr v21 xml files in data directory        
    def Process(self):
        files = glob.glob(os.path.join(self._data_dir, "*.XML"))
        files.sort(key=os.path.getmtime)    # process in asc order
        for filepath in files:
            self._tumors.clear()
            logging.info(f"[processing {filepath}]")
            tree = et.parse(filepath)
            root = tree.getroot()
            hi = self.ParseHeaderFields(root)
            logging.info(f"- parsing XML")
            self.ParseTumors(root, hi)
            logging.info(f"- saving tumors")
            self.SaveTumors()
            self.MoveFile(filepath)

    def ParseHeaderFields(self, root):
        hi = HeaderInfo()
        nodes = [x for x in root if x.tag == "{http://naaccr.org/naaccrxml}Item"]
        for node in nodes:
            setattr(hi, node.attrib.get("naaccrId"), node.text)
        return hi

    def ParseTumors(self, root, headerInfo):
        patients = [x for x in root if x.tag == "{http://naaccr.org/naaccrxml}Patient"]
        for patient in patients:
            tumors = [x for x in patient if x.tag == "{http://naaccr.org/naaccrxml}Tumor"]
            for tumor in tumors:
                ti = TumorItem()
                for k, v in headerInfo.__dict__.items():
                    setattr(ti, k, v.strip() if v else "")
                nodes = [x for x in tumor if x.tag == "{http://naaccr.org/naaccrxml}Item"]
                for node in nodes:
                    setattr(ti, node.attrib.get("naaccrId"), node.text.strip() if node.text else "")
                nodes = [x for x in patient if x.tag == "{http://naaccr.org/naaccrxml}Item"]
                for node in nodes:
                    setattr(ti, node.attrib.get("naaccrId"), node.text.strip() if node.text else "")
                self._tumors.append(ti)

    def SaveTumors(self):
        qty = 0
        sql, keys = self.GenerateInsertSQL()
        conn = sqlite3.connect('naaccr_data.db')
        cursor = conn.cursor()
        for tumor in self._tumors:
            if self.MostRecentTumor(conn, tumor):
                values = []
                for key in keys:
                    if hasattr(tumor, key) == True:
                        attribute = getattr(tumor, key)
                        if self.MaxLength(key, attribute) == False:
                            attribute = None # set filed value to null if too long
                        values.append(attribute)
                    else:
                        values.append(None)
                self.DeleteTumor(conn, tumor)
                cursor.execute(sql, values)
                conn.commit()
                qty = qty + 1 
        logging.info(f"[number of XML items saved]: {qty}")

    def MostRecentTumor(self, conn, tumor):
        # note: expects key fields medicalRecordNumber, tumorRecordNumber, registryId, dateCaseReportExported to exist
        # if medicalRecordNumber doesn't exist, patientIdNumber will be used instead. if this doesn't exist, empty string will be used. 
        # if dateCaseReportExported doesn't exist, dateCaseLastChanged will be used instead. if this doesn't exist, empty string will be used.  
        # you may need to change to the code to accommodate your field names as needed
        params = (getattr(tumor,"medicalRecordNumber", getattr(tumor,"patientIdNumber", "")), 
            getattr(tumor, "tumorRecordNumber"), getattr(tumor, "registryId"), getattr(tumor, "dateCaseReportExported", getattr(tumor,"dateCaseLastChanged", "")))
        sql = """select * from NAACCR_DATA 
            where MEDICAL_RECORD_NUMBER_N2300 = ? and TUMOR_RECORD_NUMBER_N60 = ? and REGISTRY_ID_N40 = ?
            and DATE_CASE_REPORT_EXPORT_N2110 > ?"""
        cmd = conn.cursor()
        cmd.execute(sql, params)
        row = cmd.fetchone()
        if row is None:
            return True
        return False

    def DeleteTumor(self, conn, tumor):
        # note: expects key fields medicalRecordNumber, tumorRecordNumber, registryId to exist
        # if medicalRecordNumber doesn't exist, patientIdNumber will be used instead. if this doesn't exist, empty string will be used.  
        # you may need to change to the code to accommodate your field names as needed
        params = (getattr(tumor,"medicalRecordNumber", getattr(tumor,"patientIdNumber", "")), getattr(tumor, "tumorRecordNumber"), getattr(tumor, "registryId"))
        sql = """delete from NAACCR_DATA 
            where MEDICAL_RECORD_NUMBER_N2300 = ? and TUMOR_RECORD_NUMBER_N60 = ? and REGISTRY_ID_N40 = ?"""
        cmd = conn.cursor()
        cmd.execute(sql, params)
        conn.commit()

    # build sql insert based on columns in field mapping
    def GenerateInsertSQL(self):
        keys = []
        fields1 = ""
        fields2 = ""
        for key in self._fieldmapping:
            keys.append(key)
            if fields1 == "":
                fields1 = self._fieldmapping[key]
                fields2 = "?"
            else:
                fields1 = fields1 + ", " + self._fieldmapping[key]
                fields2 = fields2 + ", ?"
        sql = f"insert into NAACCR_DATA ({fields1}) values ({fields2})"
        return (sql, keys)

    # move file to processed directory after processed
    # note:  processed directory is cleared each time on each run
    def MoveFile(self, filepath):
        if not os.path.exists(self._processed_dir):
            os.makedirs(self._processed_dir)
        os.rename(filepath, os.path.join(self._processed_dir, os.path.basename(filepath)))

    # validate max field length based on column mapping config in mapping.py
    def MaxLength(self, key, attribute):
        dbfield = self._fieldmapping[key]
        maxlen = self._columnmapping[dbfield]
        if len(attribute) > maxlen:
            print(f"value too long - column: {key}, value: {attribute}, maxlen: {maxlen}")
            return False
        return True



    
