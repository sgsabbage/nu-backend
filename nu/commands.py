import datetime
import importlib
import pkgutil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import nu.plugins
from nu.core.channels.models import Channel, ChannelCharacter, ChannelMessage
from nu.core.config import settings
from nu.core.grid.models import Area, Exit, Room, RoomStatus
from nu.core.player.models import Character, Permission, Player, PlayerWindow, Role
from nu.db.base_class import metadata
from nu.plugins.health import CharacterHealthModel, HasHealth

for _, name, is_pkg in pkgutil.iter_modules(
    nu.plugins.__path__, nu.plugins.__name__ + "."
):
    importlib.import_module(name)


def init_db() -> None:
    assert settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    to_add = []
    r = Role(
        name="Admin",
        permissions=[
            Permission.CHANNEL_CREATE,
            Permission.CHANNEL_DELETE,
        ],
    )
    r2 = Role(
        name="Channel Stuff",
        permissions=[Permission.CHANNEL_DELETE, Permission.CHANNEL_UPDATE],
    )
    p = Player(
        username="Ifrit", password="p123", email="notanemail@example.com", roles=[r, r2]
    )
    c = Character(name="Afanc", player=p, base_color="#007ea8")
    c3 = Character(name="Ifrit", player=p, base_color="#804000")
    c2 = Character(name="Rathenhope", player=p)
    p2 = Player(username="Player", password="p123", email="notanemail2@example.com")
    assert isinstance(Character, HasHealth)
    c12 = Character(
        name="PC", player=p2, base_color="#7e00a8", health=CharacterHealthModel(hp=10)
    )

    to_add.extend([p, c, c3, c2, p2, c12, r, r2])

    pub = Channel(name="Public", description="The public channel")
    admin = Channel(name="Admin", description="The admin channel")
    plotting = Channel(name="Plotting", description="A channel for plots")

    london = Area(name="London")
    private_club = Room(
        name="Private Club", status=RoomStatus.PRIVATE, area=london, x=0, y=-2
    )
    centre = Room(name="City Centre", status=RoomStatus.PUBLIC, area=london, x=0, y=0)
    north = Room(
        name="North London",
        description="This is North London. It looks very north.",
        status=RoomStatus.PUBLIC,
        area=london,
        x=0,
        y=-1,
    )
    south = Room(name="South London", status=RoomStatus.PUBLIC, area=london, x=0, y=1)
    east = Room(name="East London", status=RoomStatus.PUBLIC, area=london, x=-1, y=0)
    west = Room(name="West London", status=RoomStatus.PUBLIC, area=london, x=1, y=0)
    secret = Room(name="Secret London", status=RoomStatus.SECRET, area=london, x=0, y=4)

    c.current_room = south
    c2.current_room = north
    c3.current_room = west
    c12.current_room = north

    Exit(start_room=centre, end_room=north, name="North")
    Exit(start_room=centre, end_room=south, name="South")
    Exit(start_room=centre, end_room=east, name="East")
    Exit(start_room=centre, end_room=west, name="West")
    Exit(start_room=south, end_room=secret, name="SECRET", secret=True)
    Exit(start_room=west, end_room=north, name="shortcut")
    Exit(start_room=east, end_room=south, secret=True, name="shortcut")
    Exit(start_room=north, end_room=private_club, name="club")

    to_add.extend([pub, admin, plotting, london, centre, north, private_club])

    to_add.append(ChannelCharacter(character=c, channel=admin))
    to_add.append(ChannelCharacter(character=c, channel=pub))
    to_add.append(ChannelCharacter(character=c2, channel=pub))
    to_add.append(ChannelCharacter(character=c2, channel=plotting))
    to_add.append(ChannelCharacter(character=c3, channel=pub))
    to_add.append(ChannelCharacter(character=c3, channel=admin))
    to_add.append(ChannelCharacter(character=c3, channel=plotting))
    to_add.append(ChannelCharacter(character=c12, channel=pub))

    PlayerWindow(
        player=p,
        name="Map",
        width=300,
        height=800,
        top=0,
        left=1000,
        position=0,
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
        position=1,
        character=c2,
    )
    PlayerWindow(
        player=p,
        name="Boards",
        width=500,
        height=400,
        top=0,
        left=0,
        position=2,
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
        position=3,
        component="Channels",
        character=c,
    )
    PlayerWindow(
        player=p,
        name="Channels2",
        width=500,
        height=400,
        top=400,
        left=500,
        position=4,
        component="Channels",
        character=c,
    )
    PlayerWindow(
        player=p,
        name="Character",
        width=500,
        height=400,
        top=0,
        left=500,
        position=5,
        component="Character",
        character=c2,
    )
    PlayerWindow(
        player=p2,
        name="Channels",
        width=500,
        height=400,
        top=0,
        left=500,
        position=0,
        component="Channels",
        character=c12,
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
