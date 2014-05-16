"""

Template for Objects

Copy this module up one level and name it as you like, then
use it as a template to create your own Objects.

To make the default commands default to creating objects of your new
type (and also change the "fallback" object used when typeclass
creation fails), change settings.BASE_OBJECT_TYPECLASS to point to
your new class, e.g.

settings.BASE_OBJECT_TYPECLASS = "game.gamesrc.objects.myobj.MyObj"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Object as DefaultObject
from ev import Object
from ev import Command
import textwrap
import math

from game.gamesrc.commands.cmdset import ChapterCmdSet
from src.utils.evtable import EvTable

# Support function to chunk a list
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class Chapter(Object):
    """
    This is a chapter object.  It's designed to be inserted into
    a book object. Ideas of unique qualities a chapter might contain:

        * Chapter number
        * Chapter title
        * Chapter summary?
        * List of strings representing content-filled pages
        * Total existing number of pages

    Not yet decided:
        * Material (common to all objects? push a level up?)
        * Max # pages (especially if players are allowed to create books)
        * Max content per page


    """
    def at_object_creation(self):
        "This runs at creation time.  Use in lieu of __init__"
        
        # Store a default description, can change at creation time.
        desc = "This is a collection of pages organized into a chapter "
        desc += "entitled: %s." % self.key

        # Set our chapter attributes
        self.db.desc = desc
        self.db.chapter_num = 0
        self.db.chapter_title = "Test Title"
        self.db.chapter_summary = ""
        self.db.content = ["Testing1"]
        self.db.total_pages = 0

        # Add command sets
        self.cmdset.add(ChapterCmdSet, permanent=True)

        # Here we'll want to add commands specific to chapters

    def edit_ch_num(self):
        pass

    def add_page(self):
        pass

    def edit_page(self):
        pass

    def delete_page(self):
        pass

    def display_page(self):
        """
        Displays chapter text using EvTable

        Here we'll break chapter text up into chunks to be displayed in EvTables with
        a single column, three rows, and defined width and height for "book-like" 
        readability. The heading contains the book title, if any, followed by the 
        chapter number and name. The middle row contains the chapter text, wrapped
        approprirately for readability. The third row contains the page number.

        Since the table will have defined height, chapter content should fill an
        EvTable ("page") and be able to overflow into subsequent "pages", with
        some mechanism for the user to cycle through pages.

        While EvTable is fantastic, it simply truncates a long string of text that 
        doesn't fit within a cell height, with no ability to access the overflow
        text.  Because of this, we'll pre-process our text string to determine how
        manu "chunks" of text we'll need in order to structure our pages. Since
        a cell has a defined width, and the height of a cell is defined as the 
        number of lines it has room for, this makes it possible to pre-process
        our chapter content to fill the EvTables.  This pre-processing should 
        basically mirror the functionality in EvTable, breaking the string up
        into chunks of same width and number of lines as EvTable would for the
        content cell.
        """
        # Build the text for our header row, two lines
        book_title = "*** Arise ***".upper()
        heading = book_title + "\nCh. %s: %s" % (self.db.chapter_num, self.db.chapter_title)

        # Sample content for testing. In-game chapter content creation will involve
        # input on a single line (the text input field). Suggest user help text that
        # directs them to use a newline characters and three spaces to set apart.
        """
        content = "ONCE upon a time there was some test content. It was long, and crazy."
        content += " We did some more test content here, to see if it wraps properly."
        content += " The test content endeavored to wrap improperly, but subsequently was "
        content += "conquered, and thus wrapped properly. And so it was. And it was good. "
        content += "This doesn't start a new line. This is some more filler content. "
        content += "This overflows to a second page if height is 5. This is even more "
        content += "filler content here. Yessssssssssssssssssssssssssssssssssssss! "
        content += "filler content here. Yessssssssssssssssssssssssssssssssssssss! "
        content += "filler content here. Yessssssssssssssssssssssssssssssssssssss! "
        content += "filler content here. Yessssssssssssssssssssssssssssssssssssss! "
        content += "filler content here. Yessssssssssssssssssssssssssssssssssssss! "
        content += "filler content here. Yessssssssssssssssssssssssssssssssssssss! "
        
        content = "  First line.\n\n"
        content += "Second line.\n\n"
        content += "Third line.\n\n"
        content += "Fourt line.\n\n"
        content += "Fifth line."
        """

        # Set some chapter display variables
        ch_width = 14
        ch_hpadding = 1*2       #left and right padding
        ch_border = 1*2         #left and right border
        ch_text_width = ch_width - (ch_hpadding + ch_border)
        ch_content_height = 10  #20 lines of text max in content cell

        
        content = "This is a line.\n\n  This is another. More text."
        # I want it to split at the new lines and KEEP new line character
        # list = ["This is a line.\n", "\n", "  This is another. More text."]
        # If width is 20, what's the height of this? 

        table = EvTable(heading, border="table", width=ch_width, enforce_size=True)
        table.add_row(content, align="l", border_top_char="~", height=ch_content_height, valign="t")
        table.add_row(("Pg. %s" % 1), align="c", valign="b")

        print table














        """
        Next we'll pre-process our text, wrapping to a given width and breaking into lines.
        Interestingly, Python textwrap.wrap() doesn't properly handle newlines.  This 
        list comprehension is a workaround that honors even multiple newlines.
        Poached from: http://bugs.python.org/msg166629.  Thanks to that person.
        """
        text_chunks = [line for para in content.splitlines(False) for line in 
            textwrap.wrap(para, ch_text_width, replace_whitespace=False) or ['']]

        # What the above is doing:
        # ['   Start of paragraph, one line, then newline.\n', 'Second line.']
        # First for loop: '   Start of paragraph, one line, then newline.\n'

        print "Split: ", content.splitlines(False)

        # How many pages will we need, and how many overflow lines on last pg?
        num_pages = int(math.ceil(len(text_chunks) / float(ch_content_height)))
        overflow = len(text_chunks) % ch_content_height

        # Print to console to see if this mirrors EvTable functionality   
        print "text_chunks: ", text_chunks
        print len(text_chunks)
        print "Pages: %s" % num_pages
        print "Overflow: %s" % overflow

        # A list of EvTables representing the pages of the chapter
        ch_pages = []
                
        # Build the table. Heading cell text centered, content cell text
        # left and top aligned, bottom cell text centered.
        for group in chunker(text_chunks, ch_content_height):
            print "Group: ", group
            
            ev_string = ""

            for item in group:
                if not item:
                    ev_string += "\n"
                else:
                    ev_string += item

            #group = ' '.join(group)

            page_num = len(ch_pages) + 1

            table = EvTable(heading, border="table", width=ch_width, enforce_size=True)
            table.add_row(ev_string, align="l", border_top_char="~", height=ch_content_height, valign="t")
            table.add_row(("Pg. %s" % page_num), align="c", valign="b")

            print table
            ch_pages.append(table)
        
        print "ch_pages: ", ch_pages
        return ch_pages



    


class Object(DefaultObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved to
                           database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     dbobj (Object, read-only) - link to database model. dbobj.typeclass points
                                  back to this class
     typeclass (Object, read-only) - this links back to this class as an
                         identified only. Use self.swap_typeclass() to switch.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     player (Player) - controlling player (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       player above)
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     sessions (list of Sessions, read-only) - returns all sessions connected
                       to this object
     has_player (bool, read-only)- will only return *connected* players
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                             self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
                             a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, player=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get()      - this is called just before the command handler
                            requests a cmdset from this object
     at_pre_puppet(player)- (player-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (player-controlled objects only) called just
                            after completing connection player<->object
     at_pre_unpuppet()    - (player-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(player) - (player-controlled objects only) called just
                            after disconnecting player<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_before_traverse(traversing_object)                 - (exit-objects only)
                              called just before an object traverses this object
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

     """
    pass