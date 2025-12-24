from sms_ir import SmsIr


api_key = "NFwDOyzDoUCVBxB2CSlO374WlXOAeaKGST1ubHFziSEcLbhf"
linenumber = "300790"

def verify_send_sms(number:str,template_id:str,code:str):
    try:
        template_id = str(template_id)
        parameters = [
            {"name": "CODE", "value": f"{code}"}
        ]
        sms_ir = SmsIr(api_key,linenumber,)
        ret = sms_ir.get_line_numbers()
        ret_ = sms_ir.send_verify_code(str(number),template_id,parameters,)
        return ret_
    except:
        return False