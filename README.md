# LastTime

_LastTime_ is to be a web-based interface to a database that will keep track of medication data pertinent to its span of effectiveness, and full elimination from the body.

## Origin

I've known that it would be handy to have something that would record administrations of different substances, whether or not they are fat soluble (extending the detectable metabolites range significantly), and appropriate half-life data, for some time now.  The original idea came about due to experience with people's issues detoxing, and knowing what substances were at play, at any given range out from the last administration, based on the administration history (at least in the case of adipose soluble substances).

## Supporting Reason

I have a friend whose doctor has done an absolutely awful job of properly administering controlled substances with addictive natures; this person is in desperate need of careful titration off of the cocktail that's been taken to wake up, stay up throughout the day, and to be able to go to sleep at night.  It turns out that after so long on such a harsh mix, there are now some pretty significant effects, including mineral/electrolyte depletion, and unsurprisingly, psychological ones, as the primary culprits affect dopamine, serotonin, and the endorphine system.

When I reflected back on this project, I realized that it could be used to help step someone in such a situation down properly.  From each of the competing substances, as the medication levels balance at the proper places, giving the body enough time to acclimate to each stage.  That's when I started developing on this in earnest.

## The Site

This project is _way_ alpha, and should not be considered even close to how it will probably end up in production.  The app separation is pretty awful, and I'm still learning Django from the very beginning.  So after I've got something fleshed out and functional, I'll come along and redesign it the right way, depending on what I have available for programming resources at that point.

### App Structure

  * **home**: app that will just handle initial navigation links and a logo/pitch page for people investigating the project
  * **subadd**: app for adding substances and their necessary chemical data to the database
  * **recadm**: app for recording administration data per usage (selecting substances added via **subadd**)
  * **dataview**: app for displaying detailed data gleaned from different substance administrations (this is where all of the gravy is at)
