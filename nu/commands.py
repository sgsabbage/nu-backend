import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nu.core.config import settings
from nu.db.base_class import metadata
from nu.models import (
    Area,
    Channel,
    ChannelCharacter,
    ChannelMessage,
    Character,
    Exit,
    Player,
    Room,
)
from nu.models.player import PlayerWindow


def init_db() -> None:
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    to_add = []
    p = Player(username="Ifrit", password="password123", email="notanemail@example.com")
    c = Character(name="Afanc", player=p, base_color="#007ea8")
    c3 = Character(name="Ifrit", player=p, base_color="#804000")
    c2 = Character(name="Rathenhope", player=p)

    to_add.extend([p, c, c3, c2])

    pub = Channel(name="Public", description="The public channel")
    admin = Channel(name="Admin", description="The admin channel")
    plotting = Channel(name="Plotting", description="A channel for plots")

    london = Area(name="London")
    centre = Room(name="City Centre", area=london, x=0, y=0)
    north = Room(name="North London", area=london, x=0, y=-1)
    south = Room(name="South London", area=london, x=0, y=1)
    east = Room(name="East London", area=london, x=-1, y=0)
    west = Room(name="West London", area=london, x=1, y=0)
    secret = Room(name="Secret London", area=london, x=0, y=4)

    Exit(start_room=centre, end_room=north, name="North")
    Exit(start_room=centre, end_room=south, name="South")
    Exit(start_room=centre, end_room=east, name="East")
    Exit(start_room=centre, end_room=west, name="West")
    Exit(start_room=south, end_room=secret, name="SECRET", secret=True)
    Exit(start_room=west, end_room=north, name="shortcut")
    Exit(start_room=east, end_room=south, secret=True, name="shortcut")

    to_add.extend([pub, admin, plotting, london, centre, north])

    to_add.append(ChannelCharacter(character=c, channel=admin))
    to_add.append(ChannelCharacter(character=c, channel=pub))
    to_add.append(ChannelCharacter(character=c2, channel=pub))
    to_add.append(ChannelCharacter(character=c2, channel=plotting))
    to_add.append(ChannelCharacter(character=c3, channel=pub))
    to_add.append(ChannelCharacter(character=c3, channel=admin))
    to_add.append(ChannelCharacter(character=c3, channel=plotting))

    PlayerWindow(
        player=p,
        name="Map",
        width=300,
        height=800,
        top=0,
        left=1000,
        z=500,
        component="Map",
        character=c2,
    )
    PlayerWindow(
        player=p,
        name="Scene",
        width=1000,
        height=400,
        top=400,
        left=0,
        z=499,
        character=c2,
    )
    PlayerWindow(
        player=p,
        name="Boards",
        width=500,
        height=400,
        top=0,
        left=0,
        z=498,
        component="BulletinBoards",
        character=c,
    )
    PlayerWindow(
        player=p,
        name="Channels",
        width=500,
        height=400,
        top=0,
        left=500,
        z=497,
        component="Channels",
        character=c,
    )

    ChannelMessage(
        character=c3,
        channel=admin,
        message=":yawns",
        timestamp=datetime.datetime.now() - datetime.timedelta(days=1),
    )
    ChannelMessage(
        character=c,
        channel=admin,
        message="No don't do that, you'll make me tired!",
        timestamp=datetime.datetime.now() - datetime.timedelta(hours=23),
    )
    ChannelMessage(
        character=c2,
        channel=pub,
        message="I really want to go to the pub.",
        timestamp=datetime.datetime.now() - datetime.timedelta(minutes=4),
    )
    ChannelMessage(
        character=c3,
        channel=pub,
        message="Well, now I do too.",
        timestamp=datetime.datetime.now() - datetime.timedelta(minutes=3),
    )
    ChannelMessage(
        character=c,
        channel=pub,
        message="Oh don't you start too...",
        timestamp=datetime.datetime.now() - datetime.timedelta(minutes=1),
    )

    maker = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    with maker() as session:
        session.add_all(to_add)
        session.commit()
