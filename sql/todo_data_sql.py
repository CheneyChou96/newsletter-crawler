insert_sql = ('insert ignore into todo_clean_data(id, task_id, title, url, publish_time, create_time, update_time, attachment) '
              'select id, task_id, title, url, publish_time, create_time, update_time, attachment from crawler_ai_news_detail')

update_sql_1 = ('update todo_clean_data t1 join crawler_ai_news_task_config t2 '
                'on t1.task_id = t2.id set t1.website_info_id = t2.website_info_id')

update_sql_2 = ('update todo_clean_data t1 join crawler_website_info t2 '
                'on t1.website_info_id = t2.id '
                'set t1.region  = t2.region,'
                't1.country = t2.country,'
                't1.subject_type = t2.subject_type,'
                't1.organization_type = t2.organization_type,'
                't1.notification_agency = t2.notification_agency,'
                't1.article_category = t2.article_category,'
                't1.regional_scope = t2.regional_scope,'
                't1.identification_source = t2.identification_source,'
                't1.website_info_id = t2.id,'
                't1.lang_site = t2.language_locale,'
                't1.lang = t2.language')
