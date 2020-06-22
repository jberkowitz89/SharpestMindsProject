class Clean_Data(db.Model):
    __tablename__ = 'cleaned_data'
    index = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    game = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    run_time = db.Column(db.DateTime, nullable=False)
    record_id = db.Column(db.String(60), nullable=False)
    scraper_run = db.Column(db.String(60), nullable=False)

    def __repr__(self):

        return 'Game: {}'.format(self.game)

    def as_dict(self):
        return {'game': self.game}