"gn" stands for "geeky notes" - console simplenote client
----------------------------------------------------------

**gn** is a CLI simplenote client written in Python. It uses Simplenote API V.2.

Before you run  **gn** you must create config file in your home directory (`~/.gn`). The format of the file is following:

    email=your@simplenote.credentials
    password=yourpassword
    editor=editor of your choice
    autosync=1
    
When `autosync` option is set to `1` or `true`, any change of notes (createing, modifying or deleting)  will be immediately synced with the server.

### gn commands are described here:

    $ gn ls            - show list of notes
    $ gn tags          - show tags
    $ gn ls 'tag'      - show notes with the tag
    $ gn [find] 'text' - search for the 'text'
    $ gn [new]         - new note
    $ gn [ed] N        - edit note N
    $ gn rm N          - delete note N
    $ gn sync [full]   - sync with simplenote
    $ gn help          - show this help
    
You can tag your notes by adding `[TAGS]: list of tags` at the end of the note in editor. If your note already has tags, you can edit them at the bottom line of the note.

Sync process is partial by default. This means that only changed since last sync will be fetched from the server. But when you're starting sync for the first time or using `sync full` command, the full sync will be performed.
                            
Copyright (c) Dmitri Brechalov, 2010-2011
