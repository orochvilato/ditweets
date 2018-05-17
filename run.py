# -*- coding: utf-8 -*-
from ditweets import app,jobs




if __name__ == "__main__":
    jobs.stop_scheduler()

    app.run(port=8889,debug=True,processes=1)
