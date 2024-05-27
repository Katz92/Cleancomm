"""
Module providing queries to interact with the db
"""
USER_SELECT_QUERY = "SELECT * FROM users WHERE email = %s"

GET_USER_BY_ID_QUERY = "SELECT * FROM users WHERE id = %s"

USER_INSERT_QUERY = """
                        INSERT INTO users (
                                    email,
                                    password,
                                    host,
                                    first_name,
                                    last_name,
                                    lang,
                                    created_date,
                                    updated_date,
                                    status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

USER_UPDATE_QUERY = """
                        UPDATE users
                        SET
                            host = %s,
                            password = %s,
                            first_name = %s,
                            last_name = %s,
                            lang = %s,
                            status = %s,
                            updated_date = %s
                        WHERE email = %s
                    """

ACTIVE_USER_SESSION_QUERY = "UPDATE users SET session_active = %s WHERE email = %s"

END_USER_SESSION_QUERY = "UPDATE users SET session_active = %s WHERE email = %s"

IS_USER_SESSION_ACTIVE_QUERY = "SELECT session_active FROM users WHERE email = %s"

NOTIF_SELECT_QUERY = "SELECT * FROM notification WHERE user_mail = %s"

NOTIF_UPDATE_QUERY = """
                        UPDATE notification
                        SET
                            daily_task_report = %s,
                            mention_in_comment = %s,
                            projet_due_date = %s,
                            projet_status_changed = %s,
                            questions_and_sections_assigned_as_author = %s,
                            questions_and_sections_assigned_as_reviewer = %s,
                            content_library_revision = %s,
                            group_of_questions_completed = %s,
                            task_assigned = %s
                        WHERE user_mail = %s
                    """
