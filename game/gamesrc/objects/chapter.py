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

"""
Support function to chunk a list

text = "I am a very, very helpful text"

for group in chunker(text, 7):
   print repr(group),
# 'I am a ' 'very, v' 'ery hel' 'pful te' 'xt'

print '|'.join(chunker(text, 10))
# I am a ver|y, very he|lpful text

animals = ['cat', 'dog', 'rabbit', 'duck', 'bird', 'cow', 'gnu', 'fish']

for group in chunker(animals, 3):
    print group
# ['cat', 'dog', 'rabbit']
# ['duck', 'bird', 'cow']
# ['gnu', 'fish']
"""
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
        heading = "Ch. %s: %s" % (self.db.chapter_num, self.db.chapter_title)

        # Sample content for testing. In-game chapter content creation will involve
        # input on a single line (the text input field). Suggest user help text that
        # directs them to use a newline characters and three spaces to set apart.
        content = "  ONCE uponnnnnnn a time there was some test content. It was long, and crazy. This is extra text to check wrapping."
        content += "\n\n   This is a new paragraph. We did some more test content here, to see if (wrap next) \n it wraps properly."
        content += "\nAnother1 line."
        content += "\n Another2 line."
        content += "\n  Another3 line."
        content += "\n   Another4 line."
        content += "\n    Another5 line."
      
        # Set some chapter display variables
        ch_width = 75
        ch_hpadding = 1*2       #left and right padding
        ch_border = 1*2         #left and right border
        ch_text_width = ch_width - (ch_hpadding + ch_border)
        ch_content_height = 10  #lines of text max in content cell
        
        """
        Next we'll pre-process our text, wrapping to a given width and breaking into lines.
        Interestingly, Python textwrap.wrap() doesn't properly handle newlines.  This 
        list comprehension is a workaround that honors even multiple newlines.
        Poached from: http://bugs.python.org/msg166629.  Thanks to that person.
        """
        # Split to honor newlines
        # Input parameter false, don't need '\n' retained because each separate list member
        #   means we've reached a '\n' character.
        # List member '' means we have a double newline and should have a completely blank line
        split_content = content.splitlines(False)
        print "Split: ", split_content

        # NOT NEEDED: FOR FUTURE DELETION AFTER COMPLETION OF MANUAL BUILD OF BOOK
        #text_chunks = [line for para in split_content for line in 
            #textwrap.wrap(para, ch_text_width, replace_whitespace=False) or ['']]

        # Build a new list that wraps each line to our width, or in the case of empty string, adds a blank line
        # Example list: ['ONCE upon a time there was some test content. It was long, and crazy., '', ' We did some more test content here, to see if it wraps properly.']
        # For member in list, if member has text, wrap it to our width, add to new list, else add completely blank line to list
        wrapped_content = []
        for member in split_content:
            if member:
                wrapped_content.extend(textwrap.wrap(member, ch_text_width, replace_whitespace=False))
            else:
                wrapped_content.append(' ' * ch_text_width)

        # Now we have a list of properly-wrapped lines. 
        # Let's chunk our list into pieces that will fit in our desired content cell height.
        # This should create a list of lists of strings
        the_pages = chunker(wrapped_content, ch_content_height)

        
        """
        Build our chapter display line by line, with a header, content, and page num section.
        Our wrapped_content[] should already contain a properly-wrapped list of lines
        """
        pages_display = []
        pg_num = 0

        for group in the_pages:                 # For list of strings in list of lists of strings
            print "In for loop."
            ch_display = ""
            pg_num += 1

            # Calculation to center the text in the heading
            btitle_leading = (ch_width - ch_hpadding - len(book_title)) / 2
            btitle_trailing = (ch_width - ch_hpadding - len(book_title)) - btitle_leading
            bheading_leading = (ch_width - ch_hpadding - len(heading)) / 2
            bheading_trailing = (ch_width - ch_hpadding - len(heading)) - bheading_leading

            # Build the heading
            ch_display += "+%s+\n" % ("-" * (ch_width - ch_border))
            ch_display += "|%s%s%s|\n" % (" "*btitle_leading, book_title, " "*btitle_trailing)
            ch_display += "|%s%s%s|\n" % (" "*bheading_leading, heading, " "*bheading_trailing)
            ch_display += "+%s+\n" % ("~" * (ch_width - ch_border))

            # Build the content cell. This should generally honor formatting and newlines.
            for line in group:
                endspace = ch_text_width - len(line)
                ch_display += "| %s%s |\n" % (line, (" "*endspace))

            # If our content is less height than allowed, add blank lines to page
            # Pages should be of uniform height even if there's not enough text to fill
            leftover = ch_content_height - len(group)
            while leftover > 0:
                ch_display += "|%s|\n" % (" "*(ch_width - ch_border))
                leftover -= 1

            # Build final lines and pg number
            pg_display = "Pg. %s" % pg_num
            bpage_leading = (ch_width - ch_hpadding - len(pg_display)) / 2
            bpage_trailing = (ch_width - ch_hpadding - len(pg_display)) - bpage_leading
            ch_display += "|%s%s%s|\n" % (" "*bpage_leading, pg_display, " "*bpage_trailing)
            ch_display += "+%s+\n" % ("-" * (ch_width - ch_border))

            print ch_display
            pages_display.append(ch_display)

        print "Out of loop"
        return pages_display

        # How many pages will we need, and how many overflow lines on last pg?
        #num_pages = int(math.ceil(len(text_chunks) / float(ch_content_height)))
        #overflow = len(text_chunks) % ch_content_height



    


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