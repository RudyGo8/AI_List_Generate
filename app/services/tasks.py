'''
@create_time: 2026/3/28 涓婂崍11:10
@Author: GeChao
@File: tasks.py
'''
import datetime
import time
import json

import requests

from app.config import logger
from app.database import get_db_instance
from app.models.constants import DataStatus, SpecialID, BatchType, NoticeStatus
from app.models.db_notice_detail import DbNoticeDetail
from app.models.db_product_des_detail import ProductDesDetail
from app.models.db_product_src_detail import ProductSrcDetail
from app.models.db_product_task_detail import DbProductTaskDetail
from app.services.llm import get_model_used
from app.services.shop import shop_product_category, shop_product_bundle_text_only
from app.utils.param_utils import list_url_to_str, usage_addition, list_to_str, filter_product_response, json_serial


def _get_scene_from_custom_data(custom_data):
    if not custom_data:
        return 'default'

    try:
        payload = json.loads(custom_data) if isinstance(custom_data, str) else custom_data
        if isinstance(payload, dict):
            return payload.get('ai_scene', 'default')
    except Exception:
        return 'default'

    return 'default'


def set_product_src_to_db(clientId,
                          spu_image_url,
                          sku_image_url_list,
                          notice_url,
                          platform_id,
                          site,
                          product_title,
                          category_id,
                          category_name,
                          attributes,
                          tag_type,
                          custom_data,
                          des_lang_type):
    """瀛樺偍鍘熷鍟嗗搧鏁版嵁鍒版暟鎹簱"""
    db_instance = next(get_db_instance())
    try:
        new_product_src = ProductSrcDetail(
            gid=clientId,
            spu_image_url=spu_image_url,
            sku_image_url_list=list_url_to_str(sku_image_url_list),
            product_title=product_title,
            category_id=category_id,
            category_name=category_name,
            attributes=json.dumps(attributes, ensure_ascii=False) if attributes is not None else None,
            create_user=clientId,
            update_user=clientId
        )

        db_instance.add(new_product_src)
        db_instance.commit()
        db_instance.refresh(new_product_src)
        product_src_id = new_product_src.id

        new_gen_task = DbProductTaskDetail(
            gid=clientId,
            product_src_id=product_src_id,
            platform_id=platform_id if platform_id is not None else -1,
            notice_url=notice_url,
            site=site,
            tag_type=tag_type,
            status=DataStatus.READY.value,
            custom_data=custom_data,
            des_lang_type=des_lang_type
        )

        db_instance.add(new_gen_task)
        db_instance.commit()
        db_instance.refresh(new_gen_task)

        return True, new_gen_task.id
    except Exception as error:
        logger.error(error)
        return False, SpecialID.NOTHING.value
    finally:
        db_instance.close()


def set_product_des_to_db(clientId, site, platform_id, product_src_id, model_name,
                          product_title, product_desc, spu_image_url, sku_image_url_list, category_name, category_id,
                          tag_value, sales_attr_value_list, attr_value_list, duration, usage, remark, db_instance):
    """Store generated product data into database."""
    try:
        llm_model = get_model_used(task_type='shop_desc')

        new_product_des = ProductDesDetail(
            gid=clientId,
            platform_id=platform_id,
            site=site,
            product_src_id=product_src_id,
            product_title=product_title,
            product_desc=product_desc,
            spu_image_url=spu_image_url,
            sku_image_url_list=list_to_str(sku_image_url_list),
            category_id=category_id,
            category_name=category_name,
            sales_attr_value_list=sales_attr_value_list,
            attr_value_list=attr_value_list,
            tag_value=tag_value,
            remark=remark,
            create_user=clientId,
            update_user=clientId
        )

        db_instance.add(new_product_des)
        db_instance.commit()
        db_instance.refresh(new_product_des)

        if product_src_id:
            existing_task = db_instance.query(DbProductTaskDetail).filter_by(
                product_src_id=product_src_id,
                platform_id=platform_id,
                gid=clientId,
                site=site
            ).first()
            if existing_task:
                existing_task.product_des_id = new_product_des.id
                existing_task.model_name = model_name if model_name else llm_model
                existing_task.duration = duration
                existing_task.usage = json.dumps(usage, ensure_ascii=False) if usage else None
                existing_task.status = DataStatus.SUCCESS.value
                existing_task.update_user = clientId
                db_instance.commit()

        return True, new_product_des
    except Exception as error:
        logger.error(error)
        return False, None


def shop_product_generate_wrapper(task_record_id, batch_no):
    session_for_thread = next(get_db_instance())
    if not task_record_id:
        logger.info(f"task_record is None, Nothing to do")
        return True
    task_record = session_for_thread.query(DbProductTaskDetail).filter_by(id=task_record_id).first()
    if not task_record:
        logger.info(f"task_record not found, task_record_id={task_record_id}")
        session_for_thread.close()
        return False

    product_src = session_for_thread.query(ProductSrcDetail).filter_by(id=task_record.product_src_id, gid=task_record.gid).first()
    if not product_src:
        logger.info(f"product_src not found, task_record_id={task_record_id}, product_src_id={task_record.product_src_id}")
        task_record.status = DataStatus.FAIL.value
        session_for_thread.commit()
        session_for_thread.close()
        return False

    scene = _get_scene_from_custom_data(task_record.custom_data)
    llm_model = get_model_used(task_type='shop_desc', scene=scene)

    try:
        task_record.status = DataStatus.PROCESSING.value
        session_for_thread.commit()

        usage_total = None
        start_time = time.time()
        # 1) generate category
        des_product_category, usage = shop_product_category(site=task_record.site,
                                                            spu_image_url=product_src.spu_image_url,
                                                            sku_image_url_list=product_src.sku_image_url_list,
                                                            product_title=product_src.product_title,
                                                            category_name=product_src.category_name,
                                                            db_instance=session_for_thread,
                                                            scene=scene)
        if des_product_category is None:
            des_product_category = {"category_path": "General", "category_id": "DEFAULT"}
        usage_total = usage_addition(usage_total, usage)

        # 2) generate title/description/attributes in one text-only call
        bundle_result, usage = shop_product_bundle_text_only(
            product_title=product_src.product_title,
            category_name=des_product_category.get('category_path', 'General'),
            attributes=product_src.attributes,
            db_instance=session_for_thread,
            des_lang_type=task_record.des_lang_type,
            scene=scene
        )
        usage_total = usage_addition(usage_total, usage)

        if not bundle_result:
            bundle_result = {}
        des_product_title = bundle_result.get("product_title") or "Generated Title"
        des_product_desc = bundle_result.get("product_desc") or "Generated Description"
        des_product_attribute = bundle_result.get("attributes") or "{}"

        end_time = time.time()
        duration = end_time - start_time

        # 5) persist generated data
        title_to_save = str(des_product_title)[:250] if des_product_title else "Product"
        desc_to_save = str(des_product_desc)[:5000] if des_product_desc else "Description"
        attr_to_save = str(des_product_attribute)[:5000] if des_product_attribute else "{}"

        res, product_des = set_product_des_to_db(clientId=task_record.gid, site=task_record.site,
                                                 platform_id=task_record.platform_id,
                                                 product_src_id=product_src.id, model_name=llm_model,
                                                 product_title=title_to_save, product_desc=desc_to_save,
                                                 spu_image_url=product_src.spu_image_url,
                                                 sku_image_url_list=product_src.sku_image_url_list,
                                                 category_name=des_product_category.get("category_path", "General"),
                                                 category_id=des_product_category.get("category_id", "DEFAULT"),
                                                 tag_value=None,
                                                 sales_attr_value_list=None,
                                                 attr_value_list=attr_to_save, duration=duration,
                                                 usage=usage_total,
                                                 remark=f"鐢?{llm_model} 鐢熸垚",
                                                 db_instance=session_for_thread)
        if not res:
            return False

        # 6) optional callback notification
        if task_record.notice_url:
            notice_content = product_des.to_dict()
            res = notice_wrapper(gid=task_record.gid, task_type=BatchType.PRODUCT_GENERATE.value,
                                 biz_id=product_des.id, notice_content=notice_content, batch_no=batch_no,
                                 notice_url=task_record.notice_url, custom_data=task_record.custom_data,
                                 db_instance=session_for_thread, task_id=task_record.id)
            if not res:
                logger.info(f'create notice record error! product_des_id = {product_des.id}')

        task_record.status = DataStatus.SUCCESS.value
        session_for_thread.commit()
        logger.info(f"Task completed: product_src_id={product_src.id}, product_des_id={product_des.id}, batch_no={batch_no}")
        return True

    except Exception as e:
        logger.info(f"Error processing task ID={task_record_id}: {e}")
        session_for_thread.rollback()
        try:
            task_record.status = DataStatus.FAIL.value
            session_for_thread.commit()
        except Exception:
            session_for_thread.rollback()
        return False
    finally:
        session_for_thread.close()


def notice_wrapper(gid, task_type, biz_id, notice_content, batch_no, notice_url, db_instance, custom_data=None,
                   notice_id=None, task_id=None):
    if notice_id:
        record = db_instance.query(DbNoticeDetail).filter_by(id=notice_id).first()
        if not record:
            logger.info('notice_id is not in DbNoticeDetail')
            return False
    else:
        if not notice_url or not notice_content or not biz_id or not task_type or not gid:
            logger.info('lose parameters!')
            return False
        record = DbNoticeDetail(
            gid=gid,
            task_type=task_type,
            biz_id=biz_id,
            notice_url=notice_url,
            notice_content=json.dumps(notice_content, ensure_ascii=False, default=json_serial),
            custom_data=custom_data,
            notice_counts=0,
            batch_no=batch_no,
            status=NoticeStatus.PROCESSING.value
        )
        db_instance.add(record)
        db_instance.commit()
        db_instance.refresh(record)

    try:
        record.status = NoticeStatus.PROCESSING.value
        headers = {
            'Content-Type': 'application/json'
        }
        notice_content = json.loads(record.notice_content)
        notice_content['task_id'] = notice_content.get('task_id') or task_id
        notice_content['custom_data'] = record.custom_data
        notice_content = filter_product_response(notice_content)
        response = requests.post(record.notice_url, headers=headers, json=notice_content)
    except Exception as error:
        record.remark = str(error)
        response = None

    if response and response.status_code == 200:
        record.status = NoticeStatus.SUCCESS.value
        record.remark = 'success'
        ret = True
    else:
        record.remark = f'notice_url return {response.status_code}' if not record.remark else record.remark
        record.next_notice_time = get_next_notice_time(notice_counts=record.notice_counts,
                                                       next_notice_time=record.next_notice_time)
        record.notice_counts = record.notice_counts + 1
        if record.status == NoticeStatus.PROCESSING.value and record.notice_counts > 12:
            record.status = NoticeStatus.FAIL.value
        ret = False
    db_instance.commit()
    return ret


def get_next_notice_time(notice_counts, next_notice_time):
    if next_notice_time is None:
        next_notice_time = datetime.datetime.now()
    additional_seconds = 2 ** notice_counts * 60
    next_notice_time = next_notice_time + datetime.timedelta(seconds=additional_seconds)
    return next_notice_time


def get_product_des_by_task(task_id):
    db_instance = next(get_db_instance())

    if not task_id:
        return DataStatus.FAIL.value, None, None, None

    try:
        task_record = db_instance.query(DbProductTaskDetail).filter_by(id=task_id).first()
        if not task_record:
            return DataStatus.FAIL.value, None, None, None

        if task_record.status == DataStatus.SUCCESS.value:
            product_des_record = db_instance.query(ProductDesDetail).filter_by(id=task_record.product_des_id).first()
            return task_record.status, product_des_record, task_record.usage, task_record.model_name

        return task_record.status, None, None, task_record.model_name
    except Exception as error:
        logger.error(error)
        return DataStatus.FAIL.value, None, None, None
    finally:
        db_instance.close()

