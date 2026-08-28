import pandas as pd
import io
from typing import List, Dict, Any, Tuple
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from fastapi.responses import StreamingResponse

from app.utils.jalali import parse_jalali_date

class ExcelService:
    @staticmethod
    def generate_template(import_type: str) -> bytes:
        """تولید قالب Excel بر اساس نوع عملیات"""
        wb = Workbook()
        ws = wb.active
        
        # ستون‌ها بر اساس نوع
        if import_type == "DEBIT":
            columns = ["شماره عضو", "نام کامل", "مبلغ (ریال)", "شرح"]
            sample_data = [
                ["010001", "علی محمدی", "50000000", "قسط اول"],
                ["010002", "رضا احمدی", "30000000", "قسط اول"],
            ]
        elif import_type == "CREDIT":
            columns = ["شماره عضو", "نام کامل", "مبلغ (ریال)", "شرح"]
            sample_data = [
                ["010001", "علی محمدی", "30000000", "وام خرید"],
                ["010002", "رضا احمدی", "25000000", "وام خرید"],
            ]
        elif import_type == "MEMBER":
            columns = ["شماره عضو", "نام کامل", "کد ملی", "موبایل", "تلفن", "آدرس"]
            sample_data = [
                ["010001", "علی محمدی", "1234567890", "09121234567", "", ""],
                ["010002", "رضا احمدی", "9876543210", "09127654321", "", ""],
            ]
        elif import_type == "BANK_STATEMENT":
            columns = ["تاریخ", "شماره حساب", "مبلغ (ریال)", "نوع", "شرح"]
            sample_data = [
                ["1404-05-03", "1234567890", "50000000", "DEPOSIT", "واریز نقدی"],
                ["1404-05-03", "1234567890", "30000000", "WITHDRAWAL", "برداشت"],
            ]
        else:
            columns = ["شماره عضو", "مبلغ (ریال)", "شرح"]
            sample_data = [["010001", "50000000", "توضیحات"]]
        
        # نوشتن هدر
        for col_idx, col_name in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # نوشتن نمونه داده
        for row_idx, row_data in enumerate(sample_data, 2):
            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        # تنظیم عرض ستون‌ها
        for col in ws.columns:
            max_length = 0
            column_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # ذخیره در حافظه
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def parse_excel(file_content: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
        """خواندن فایل Excel و تبدیل به لیست دیکشنری"""
        try:
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            data = df.to_dict(orient='records')
            
            # تشخیص ستون‌ها
            columns = df.columns.tolist()
            
            # استانداردسازی نام ستون‌ها
            column_map = {
                "شماره عضو": "member_no",
                "نام کامل": "full_name",
                "مبلغ (ریال)": "amount",
                "شرح": "description",
                "تاریخ": "date",
                "شماره حساب": "account_no",
                "نوع": "transaction_type",
                "کد ملی": "national_code",
                "موبایل": "mobile",
                "تلفن": "phone",
                "آدرس": "address"
            }
            
            # تبدیل داده‌ها
            result = []
            for row in data:
                item = {}
                for persian_col, english_col in column_map.items():
                    if persian_col in row and pd.notna(row[persian_col]):
                        value = row[persian_col]
                        # تبدیل نوع داده
                        if english_col == "amount":
                            try:
                                value = int(float(value))
                            except:
                                value = None
                        elif english_col == "date":
                            if isinstance(value, pd.Timestamp):
                                value = value.date()
                            elif isinstance(value, str):
                                try:
                                    # Dates entered in the supplied Persian template are
                                    # Jalali.  Do not let pandas reinterpret e.g. 1404 as
                                    # a Gregorian year.
                                    value = parse_jalali_date(value)
                                except ValueError:
                                    value = None
                        elif english_col == "member_no":
                            value = str(value).strip()
                        item[english_col] = value
                result.append(item)
            
            return result, []
            
        except Exception as e:
            return [], [f"خطا در خواندن فایل Excel: {str(e)}"]
    
    @staticmethod
    def create_excel_response(data: List[Dict[str, Any]], columns: List[str], filename: str):
        """ایجاد پاسخ Excel برای دانلود"""
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
