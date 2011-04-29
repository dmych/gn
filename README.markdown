"gn" stands for "geeky notes" - console simplenote client
----------------------------------------------------------

`gn` is a CLI simplenote client written in Python. It uses API V.2 (but yet does not support tags and other new functions in V.2).

Before you run  `gn` you must create config file in your home directory (`~/.gn`). The format of the file is following:

    # simplenote credentials
    email=your@simplenote.credentials
    password=yourpassword
    
    # local parameters
    editor=editor of your choice
    

### `gn` commands are described here:

    $ gn [ls]          - show list of notes
    $ gn [find] 'text' - search for the 'text'
    $ gn new           - new note
    $ gn [ed] N        - edit note N
    $ gn rm N          - delete note N
    $ gn sync          - sync with simplenote
    $ gn help          - show this help
                            
Copyright (c) Dmitri Brechalov, 2010-2011
