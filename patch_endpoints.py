with open("backend/api/endpoints.py", "r") as f:
    content = f.read()

content = content.replace("from None from None", "from None")
content = content.replace("logger = logging.getLogger(__name__)\nimport logging\n\nlogger = logging.getLogger(__name__)", "logger = logging.getLogger(__name__)")
content = content.replace("""    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve)) from None""", """    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from None""")


with open("backend/api/endpoints.py", "w") as f:
    f.write(content)
