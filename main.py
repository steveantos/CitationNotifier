from apscheduler.schedulers.background import BackgroundScheduler
from ScholarManager import ScholarManager


def update_citations_job():
    S = ScholarManager()
    S.update_all_citations()


scheduler = BackgroundScheduler()
scheduler.start()
citation_job = scheduler.add_job(update_citations_job,
                                 'cron',
                                 day_of_week='mon-fri',
                                 hour='9-16')
