#Things to do:
#- Delete thumbs after close
#- Disable Transfer related buttons when there isn't a second login
#- No thumbnail mode is suppose to make it less sluggish (when moving around window) but it doesn't because the "weight" comes from the widget count and not the image count
import tkinter as tk
import sys
import os
import threading
from tkinter.constants import ANCHOR, RIGHT
import praw
from PIL import Image, ImageTk
import urllib
import webbrowser
import tkinter.ttk as ttk
import youtube_dl
import mpv
import vlc #Significantly faster but might have problems when trying to let other people use this (will need to walk them through installing the right kind of vlc (?), I forget how I set this up)
# randomly started getting error: [0980cb78] http stream error: local stream 1 error: Cancellation (0x8) when using vlc 

#r.user.get_saved(params={'sr':'Askreddit'}) Might be able to filter during pull request rather than after 
class reddit_saved:

    def __init__(self):
        self.login_index=0
        self.deleted_list=[]
        self.logged_in=0
        self.left_logged_in=0
        self.right_logged_in=0
        self.left_imgs=[]
        self.cwd=os.getcwd()
        self.left_list=[]
        self.right_list=[]
        self.left_sub_list=[]
        self.right_sub_list=[]
        self.built_middle=0
        self.user_icons=[0,1]
        self.right_imgs=[]
        self.last_widget=0
        self.left_index=0
        self.right_index=0
        self.generation_flag=0
        self.b_generation_flag=0
        self.stop_generation_flag=0
        self.b_stop_generation_flag=0
        self.generate_amount=299 #999 in release, 300 for testing
        self.current_center_acc=0
        self.loop_it=0
        self.transfer_from_arrow=0
        self.target_sub="Unselected"
        self.b_target_sub="Unselected"
        self.posting_as_flag = 0
        self.posting_as_button_flipper=0
        self.sub_to_post = "Unselected"
        self.posted_count = 0
        self.generated_flag = 0
        self.page_offset = 0
        self.reverse_state = 0
        self.b_generated_flag = 0
        self.b_page_offset = 0
        self.b_reverse_state = 0
        self.use_vlc=0
        self.zoom_level = 0
        return
    
    def close(self,event):
        sys.exit(0)
        

    def clear_canvas(self): #Clear post feed, recreates container, resets scrollbar
        
        self.canvas.yview_moveto('0')
        
        
        try:
            self.canvas.move(self.frame_thumbs_id,400,0)
            self.canvas.xview_moveto('0')
            
        except:
            print("bruh")
        
        #self.frame_thumbs.destroy()
        #self.frame_thumbs.destroy() #Still too slow
        
        temp=ttk.Frame(self.canvas)
        self.frame_thumbs_id=self.canvas.create_window((0,0),window=temp,anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        #self.canvas.yview_moveto('0') 
        threading.Thread(target=self.frame_thumbs.destroy()).start 
        #self.frame_thumbs.destroy()
        self.frame_thumbs=temp
        self.left_imgs.clear()

    def b_clear_canvas(self):

        self.b_canvas.yview_moveto('0')

        try:
            self.b_canvas.move(self.b_frame_thumbs_id,400,0)
            self.b_canvas.xview_moveto('0')
        except:
            print("bruh")
        
        temp = ttk.Frame(self.b_canvas)
        self.b_frame_thumbs_id= self.b_canvas.create_window((0,0),window=temp,anchor="nw")
        self.b_canvas.config(scrollregion=self.b_canvas.bbox('all'))
        threading.Thread(target=self.b_frame_thumbs.destroy()).start
        self.b_frame_thumbs=temp
        self.right_imgs.clear()

    def link_callback(event,url): #Opens browsers on link click

        full_url = 'https://www.reddit.com' + url
        webbrowser.open_new(full_url)
          
    def on_mousewheel(self,event):
        

        try:
            if event.widget.master == self.frame_thumbs or event.widget.master.master == self.frame_thumbs: #If mousehweel event happens on Left Side.. 
                self.canvas.yview_scroll(int(-1*(event.delta/120)),'units') #Scroll the thumbnail canvas
        except:
            pass
        try:
            if event.widget.master == self.b_frame_thumbs or event.widget.master.master == self.b_frame_thumbs:
                self.b_canvas.yview_scroll(int(-1*(event.delta/120)),'units')
        except:
            pass
        
    def on_rightclick(self,event): #Right Click to hide post widget

        try:
            if event.widget.master == self.frame_thumbs:
                event.widget.destroy()
            elif event.widget.master.master==self.frame_thumbs:
                event.widget.master.destroy()
        except:
            pass
        try:
            if event.widget.master == self.b_frame_thumbs:
                event.widget.destroy()
            elif event.widget.master.master==self.b_frame_thumbs:
                event.widget.master.destroy()
        except:
            pass


    def test_remove_and_replace(self):

        the_widget_list = self.frame_thumbs.winfo_children()
        top_widget = the_widget_list[0]
        top_widget.destroy()

        ### BUILD CARD ROUTINE
        url=self.filtered_list[self.left_index].thumbnail
        title=self.filtered_list[self.left_index].title[:35]
        sub=self.filtered_list[self.left_index].subreddit.display_name
        submission = self.filtered_list[self.left_index]
        
        link=self.filtered_list[self.left_index].permalink
        displayed_link = link[:35] + '...'
        
        current_card=ttk.Frame(self.frame_thumbs)
        
        current_card.pack(anchor='nw')

        try:
            urllib.request.urlretrieve(url,'{}/thumbs/left_saved.jpg'.format(self.cwd))
        except:
            #If you can't retrieve it, it's likely a deleted post (but still can be viewed) 
            self.deleted_list.append('http://reddit.com'+self.filtered_list[self.left_index].permalink)

        img = Image.open('{}/thumbs/left_saved.jpg'.format(self.cwd))
        img.thumbnail((100,100))
        photo = ImageTk.PhotoImage(img)
        self.left_imgs.append(photo)

        current_button = ttk.Button(current_card,image=photo)
        current_button.grid(row=0,column=0,rowspan=3)
        current_button.config(command=lambda a=submission,b=current_card:self.select_card(a,b))

        current_title=ttk.Label(current_card,text=title)
        current_title.grid(row=0,column=1,sticky='w')

        current_sub=ttk.Label(current_card,text=sub)
        current_sub.grid(row=1,column=1,sticky='w')

        current_link=ttk.Label(current_card,text=displayed_link)
        current_link.grid(row=2,column=1,sticky='w')
        current_link.bind("<Button-1>",lambda event,a=link:self.link_callback(a) )
        self.left_index+=1

        ###END BULD CARD

    def flip_arrow(self,event):

        self.loop_it=0
        self.center_start_button.config(text="Start")
        self.canvas_transfer.delete('all')

        if self.transfer_from_arrow==0:
            self.transfer_from_arrow=1
            self.canvas_transfer.create_line(10,20,90,20,arrow='first',width=7,fill='black')
            self.canvas_transfer.create_line(10,50,90,50,arrow='first',width=7,fill='black')
            self.sub_to_post=self.target_sub
        else:
            self.transfer_from_arrow=0
            self.canvas_transfer.create_line(10,20,90,20,arrow='last',width=7,fill='black')
            self.canvas_transfer.create_line(10,50,90,50,arrow='last',width=7,fill='black')
            self.sub_to_post=self.b_target_sub
        
        self.sub_mode_toggle()
        

        
    def start_loop(self):

        if self.loop_it==0:
            self.loop_it=1
            self.center_start_button.config(text="Stop")
        else:
            self.loop_it=0
            self.center_start_button.config(text="Start")
    
    def automatic_func(self,side):

        if self.transfer_from_arrow == 0:
            the_widget_list = self.frame_thumbs.winfo_children()
        else:
            the_widget_list = self.b_frame_thumbs.winfo_children()
        try:
            self.last_button_auto.state(['!focus'])
        except:
            pass

        if len(the_widget_list) == 0:
            self.start_loop()
            return
        top_widget = the_widget_list[0]

        button_maybe=top_widget.winfo_children()[0]
        button_maybe.state(['focus'])
        self.last_button_auto = button_maybe
        button_maybe.invoke()
        if self.sub_mode_flag.get() == 0:
            self.transfer_post()
        else:
            self.make_post()
        

    def build_card(self,side):

        photo = self.center_img
        title =self.cc_title 
        subreddit=self.cc_subreddit
        link=self.cc_link 
        displayed_url=self.cc_displayed_url

        if side == 0:

            new_card = ttk.Frame(self.frame_thumbs)
            self.left_imgs.append(photo)

        else:

            new_card = ttk.Frame(self.b_frame_thumbs)

            self.right_imgs.append(photo)
        
        new_card_button = ttk.Button(new_card,image=photo)
        new_card_button.config(command=lambda a=self.current_center_card,b=new_card,c=side:self.select_card(a,b,c))
        new_card_button.grid(row=0,column=0,rowspan=3)
        new_card_title=ttk.Label(new_card,text=title)
        new_card_title.grid(row=0,column=1,sticky='w')

        new_card_sub=ttk.Label(new_card,text=subreddit)
        new_card_sub.grid(row=1,column=1,sticky='w')

        new_card_link=ttk.Label(new_card,text=displayed_url)
        new_card_link.grid(row=2,column=1,sticky='w')
        new_card.bind("<Button-1>",lambda event,a=link:self.link_callback(a))

        new_card.pack(anchor='nw',side='top')
    
    def hide_post(self):
        self.last_widget.destroy()

    def make_post(self):
        #TODO: crosspost vs pull url and directly post option
        #TODO: Maybe don't need two different self.target_sub's

        sub_id = self.current_center_card.id

        if self.posting_as_flag==0: #Post as Left
            poster = self.r
            unsaver = self.r2
        else:
            poster = self.r2
            unsaver = self.r
        
        to_post = poster.submission(sub_id)
        to_unsave = unsaver.submission(sub_id)

        if self.transfer_from_arrow ==0: #Transfer to right selected sub
            print("Crossposting: [", to_post.title, "] To: ", self.b_target_sub, " As : ", poster.user.me().name)
            side = 1
            try:
                to_post.crosspost(subreddit=self.b_target_sub)
                to_unsave.unsave()
            except Exception as e:
                print("Error crossposting: ",e)
            
        else: #Transfer to left selected sub
            print("CrossPosting: [", to_post.title, "] To: ", self.target_sub, " As : ", poster.user.me().name)
            side=0
            try:
                to_post.crosspost(subreddit=self.b_target_sub)
                to_unsave.unsave()
            except:
                print("Error Crossposting")
        
        self.build_card(side)

        if self.unsave_after_transfer_flag.get()==1:
            self.last_widget.destroy()

    def transfer_post(self):

        submission = self.current_center_card

        if self.current_center_acc == 0: #Left
            transfer_from = self.r
            transfer_to = self.r2
            side = 1
        else:
            transfer_from = self.r2
            transfer_to = self.r
            side = 0

        sub_id = submission.id
        to_save=transfer_to.submission(sub_id)
        to_unsave = transfer_from.submission(sub_id)
        
        print(f"Transferred Post: {to_save.title} To {transfer_to.user.me().name}'s Saved List")
        print(f"Removed Post: {to_save.title} from {transfer_from.user.me().name}'s Saved List")
        to_save.save()
        to_unsave.unsave()
        self.build_card(side)
        self.last_widget.destroy()


    def unsave_center_post(self):
            self.current_center_card.unsave()
            print("Unsaved Post: {}".format(self.current_center_card.permalink))


    def place_in_center(self,submission,side):

        self.current_center_card=submission
        self.current_center_acc=side
        

        self.cc_title = submission.title[:35]
        self.cc_subreddit = submission.subreddit.display_name
        self.cc_link = submission.permalink
        self.cc_displayed_url = submission.permalink[:35] + '...'
        self.cc_url = submission.thumbnail
        self.cc_inner_url = submission.url

        try:
            urllib.request.urlretrieve(self.cc_url,'{}/thumbs/center_thumb.jpg'.format(self.cwd))
            img = Image.open('{}/thumbs/center_thumb.jpg'.format(self.cwd))
            img.thumbnail((100,100))
            photo = ImageTk.PhotoImage(img)
            self.center_img=photo
        except:
            print("Error with ",self.cc_url)
            photo=self.placeholder_image

        self.placeholder_button.config(image=photo)
        self.placeholder_link.config(text=self.cc_displayed_url)
        self.placeholder_link.bind("<Button-1>",lambda event,a=self.cc_link:self.link_callback(a) )
        
        self.placeholder_title.config(text=self.cc_title)
        self.placeholder_sub.config(text=self.cc_subreddit)

        if side ==0:
            self.entry_pull_sub.set(self.cc_subreddit)
        else:
            self.b_entry_pull_sub.set(self.cc_subreddit)

    def select_card(self,submission,info,side):
        if self.last_widget is not 0:
            try:
                self.last_widget.config(takefocus=False)
            except:
                self.last_widget=0
        self.place_in_center(submission,side)

        self.last_widget=info
        info.config(takefocus=True)

    def stop_generation(self,side):
        if side == 0:
            self.stop_generation_flag=1
        else:
            self.b_stop_generation_flag=1
    def display_saved(self):
        self.clear_canvas()
        self.generated_flag=1

        self.display_limit = 100 #Option For Fast Load (Infinite scroll + display_limit = 10)
        self.left_index=self.page_offset
        
        self.generation_flag=1
        self.progress_bar.grid(row=0,column=0)
        count = 0
        while self.left_index < (self.display_limit+self.page_offset) and self.left_index < len(self.filtered_list) and self.stop_generation_flag==0:

            current_card=ttk.Frame(self.frame_thumbs)
            current_card.pack(anchor='nw')


            url=self.filtered_list[self.left_index].thumbnail
            title=self.filtered_list[self.left_index].title[:35]
            sub=self.filtered_list[self.left_index].subreddit.display_name
            submission = self.filtered_list[self.left_index]

            
            link=self.filtered_list[self.left_index].permalink
            displayed_link = link[:35] + '...'
            

            if self.thumbnail_flag.get() == 1:
                try:
                    urllib.request.urlretrieve(url,'{}/thumbs/left_saved.jpg'.format(self.cwd))
                    img = Image.open('{}/thumbs/left_saved.jpg'.format(self.cwd))
                    img.thumbnail((100,100))
                    photo = ImageTk.PhotoImage(img)
                    self.left_imgs.append(photo)
                except:
                    print("Urllib error")
                    print(self.filtered_list[self.left_index].permalink)
                    photo=self.placeholder_image
                try:
                    current_button = ttk.Button(current_card,image=photo)
                except:
                    return
            else:

                current_button = ttk.Button(current_card,image=self.placeholder_image)


            current_button.grid(row=0,column=0,rowspan=3)
            current_button.config(command=lambda a=submission,b=current_card,c=0:self.select_card(a,b,c))

            current_title=ttk.Label(current_card,text=title)
            current_title.grid(row=0,column=1,sticky='w')

            current_sub=ttk.Label(current_card,text=sub)
            current_sub.grid(row=1,column=1,sticky='w')

            current_link=ttk.Label(current_card,text=displayed_link)
            current_link.grid(row=2,column=1,sticky='w')
            current_link.bind("<Button-1>",lambda event,a=link:self.link_callback(a) )
            
            if self.left_index==self.page_offset:
                the_widget_list = self.frame_thumbs.winfo_children()[0]
                self.select_card(submission,the_widget_list,0)
            self.left_index+=1

        self.progress_bar['value']=count

        self.stop_generation_flag=0
        self.progress_bar.grid_remove()
        self.generation_flag=0
        sys.exit(0)

    
    def b_display_saved(self):
        self.b_clear_canvas()
        self.b_generated_flag=1

        self.display_limit=100
        self.right_index=self.b_page_offset

        self.b_generation_flag=1
        self.b_progress_bar.grid(row=0,column=1)
        count = 0
        while self.right_index < (self.display_limit+self.b_page_offset) and self.right_index < len(self.b_filtered_list) and self.b_stop_generation_flag==0:

            current_card=ttk.Frame(self.b_frame_thumbs)
            current_card.pack(anchor='nw')

            url=self.b_filtered_list[self.right_index].thumbnail
            title=self.b_filtered_list[self.right_index].title[:35]
            sub=self.b_filtered_list[self.right_index].subreddit.display_name
            submission = self.b_filtered_list[self.right_index]

            
            link=self.b_filtered_list[self.right_index].permalink
            displayed_link = link[:35] + '...'

            
            if self.b_thumbnail_flag.get()==1:
                try:
                    urllib.request.urlretrieve(url,'{}/thumbs/right_saved.jpg'.format(self.cwd))
                    img = Image.open('{}/thumbs/right_saved.jpg'.format(self.cwd))
                    img.thumbnail((100,100))
                    photo = ImageTk.PhotoImage(img)
                    self.right_imgs.append(photo)
                except:
                    print("Urllib error")
                    print(self.b_filtered_list[self.right_index].permalink)
                    photo = self.placeholder_image
                try:
                    current_button= ttk.Button(current_card,image=photo)
                except:
                    return
            else:
                current_button=ttk.Button(current_card,image=self.placeholder_image)


            current_button.grid(row=0,column=0,rowspan=3)
            current_button.config(command=lambda a=submission, b=current_card,c=1: self.select_card(a,b,c))
            
            current_title=ttk.Label(current_card,text=title)
            current_title.grid(row=0,column=1,sticky='w')

            current_sub=ttk.Label(current_card,text=sub)
            current_sub.grid(row=1,column=1,sticky='w')

            current_link=ttk.Label(current_card,text=displayed_link)
            current_link.grid(row=2,column=1,sticky='w')
            current_link.bind("<Button-1>",lambda event,a=link:self.link_callback(a))

            if self.right_index == self.b_page_offset:
                the_widget_list = self.b_frame_thumbs.winfo_children()[0]
                self.select_card(submission,the_widget_list,1)
            self.right_index+=1
            count +=1
            self.b_progress_bar['value']=count

        self.b_generation_flag=0
        self.b_progress_bar.grid_remove()
        self.b_stop_generation_flag=0
        sys.exit(0)

    def extract_save_file(self):
        with open('{}_deletedsaves.txt'.format(self.user_object.name),'w',encoding='utf-8') as f:
            print(self.deleted_list)
            for item in self.deleted_list:
                f.write("%s\n" % (item))
    
    def b_extract_save_file(self):
        with open('{}_saves.txt'.format(self.b_user_object.name),'w') as f:
            for item in self.right_list:
                f.write("%s\n" % ('https://www.reddit.com'+item.permalink))
        
    def pull_subreddits(self,side,the_list):
        for item in the_list:
            if side == 0:
                self.left_sub_list.append(item.subreddit.display_name)
            else:
                self.right_sub_list.append(item.subreddit.display_name)


    def refresh_filters(self):
        self.page_offset=0
        

        if self.reverse_flag.get() == 1:
            if (self.reverse_state==0):
                list.reverse(self.left_list)
                self.reverse_state=1
        if self.reverse_flag.get() == 0:
            if (self.reverse_state==1):
                list.reverse(self.left_list)
                self.reverse_state=0

        self.filtered_list = []
        #self.left_index=0

        for i in self.left_list:
            
            if isinstance(i,praw.models.Comment):
                continue
            
            
            if self.text_post_flag.get()==0:
                if i.is_self:
                    continue
            if self.text_post_flag.get()==1:
                if not i.is_self:
                    continue
            if self.nsfw_flag.get()== 0:
                if i.over_18:
                    continue
            if self.sfw_flag.get()==0:
                if not i.over_18:
                    continue
            
            if i.thumbnail == 'default':
                #print("Discovered a save that was deleted. The link is: https://www.reddit.com{}".format(i.permalink))
                self.deleted_list.append('https://www.reddit.com'+i.permalink)
                continue

            if i.thumbnail == 'image':
                #print("Posts from this sub don't have thumbnails.. idk what to do here bruh")
                continue
            
            

            if self.sub_flag.get()==1 and i.subreddit.display_name != self.entry_pull_sub.get():
                continue

            #if 'gfycat' in i.url:
                #print("gfycat link..")
            #    continue
            self.filtered_list.append(i)
        
        self.canvas_label.config(text="{}'s Saved List - {} Posts Found".format(self.username,len(self.filtered_list)))
        t1 = threading.Thread(target=self.display_saved)
        t1.daemon=True
        t1.start()
    
    def b_refresh_filters(self):
        self.b_page_offset = 0

        
        if self.b_reverse_flag.get() == 1:
            if (self.b_reverse_state==0):
                list.reverse(self.right_list)
                self.b_reverse_state=1
        if self.b_reverse_flag.get() == 0:
            if (self.b_reverse_state == 1):
                list.reverse(self.right_list)
                self.b_reverse_state = 0
        
        self.b_filtered_list = []
        #self.right_index=0

        for i in self.right_list:
            
            if isinstance(i,praw.models.Comment):
                continue

            if self.b_text_post_flag.get()==0:
                if i.is_self:
                    continue
            if self.b_text_post_flag.get()==1:
                if not i.is_self:
                    continue
            if self.b_nsfw_flag.get()== 0:
                if i.over_18:
                    continue
            if self.b_sfw_flag.get()==0:
                if not i.over_18:
                    continue
            
            if i.thumbnail == 'default':
                print("Discovered a save that was deleted. The link is: https://www.reddit.com{}".format(i.permalink))
                self.deleted_list.append('https://www.reddit.com'+i.permalink)
                continue
            
            if i.thumbnail == 'image':
                print("Posts from this sub don't have thumbnails.. idk what to do here bruh")
                continue
            
            
            #if i.is_crosspostable==0:
            #    continue
            
            
            if self.b_sub_flag.get()==1 and i.subreddit.display_name != self.b_entry_pull_sub.get():
                continue
            
            #if 'gfycat' in i.url:
            #    continue

            self.b_filtered_list.append(i)
        
        
        self.b_canvas_label.config(text="{} - {} Posts Found".format(self.b_username,len(self.b_filtered_list)))
        t1 = threading.Thread(target=self.b_display_saved)
        t1.daemon=True
        t1.start()

    def pull_from_subreddit(self):
        self.generation_flag=1
        if self.new_flag.get()==1:
            self.left_list = list(self.r.subreddit(self.entry_pull_sub.get()).new(limit=100))
        elif self.hot_flag.get()==1:
            self.left_list = list(self.r.subreddit(self.entry_pull_sub.get()).hot(limit=100))
        elif self.top_flag.get()==1:
            self.left_list = list(self.r.subreddit(self.entry_pull_sub.get()).top(limit=100))
        else:
            self.top_flag.set(1)
            self.left_list = list(self.r.subreddit(self.entry_pull_sub.get()).top(limit=100))

        self.left_sub_list = self.entry_pull_sub.get()
        self.entry_pull_sub.config(values=self.left_sub_list)

        self.refresh_filters()

    def b_pull_from_subreddit(self):
        self.b_generation_flag=1
        if self.b_new_flag.get()==1:
            self.right_list = list(self.r2.subreddit(self.b_entry_pull_sub.get()).new(limit=100))
        elif self.b_hot_flag.get()==1:
            self.right_list = list(self.r2.subreddit(self.b_entry_pull_sub.get()).hot(limit=100))
        elif self.b_top_flag.get()==1:
            self.right_list= list(self.r2.subreddit(self.b_entry_pull_sub.get()).top(limit=100))
        else:
            self.b_top_flag.set(1)
            self.right_list= list(self.r2.subreddit(self.b_entry_pull_sub.get()).top(limit=100))
        
        self.right_sub_list = self.b_entry_pull_sub.get()
        self.b_entry_pull_sub.config(values=self.right_sub_list)

        self.b_refresh_filters()
        
    def pull_saves(self):
        self.generation_flag=1

        self.left_list=list(self.user_object.saved(limit=self.generate_amount))

        self.left_sub_list = []
        self.pull_subreddits(0,self.left_list)
        self.left_sub_list=sorted(set(self.left_sub_list))
        self.entry_pull_sub.config(values=self.left_sub_list)


        self.refresh_filters()
    
    def b_pull_saves(self):
        self.b_generation_flag=1

        self.right_list=list(self.b_user_object.saved(limit=self.generate_amount))

        self.right_sub_list=[]
        self.pull_subreddits(1,self.right_list)
        self.right_sub_list=sorted(set(self.right_sub_list))
        self.b_entry_pull_sub.config(values=self.right_sub_list)


        self.b_refresh_filters()

    def transfer_to_sub_mode(self):

        return
    
    def set_sub(self):
        self.target_sub = self.entry_pull_sub.get()
        self.canvas_label.config(text="{}'s Subreddit: {}".format(self.username,self.target_sub))
    def b_set_sub(self):
        self.b_target_sub = self.b_entry_pull_sub.get()
        self.b_canvas_label.config(text="{}'s Subreddit: {}".format(self.b_username,self.b_target_sub))

    def posting_as_toggle(self):
        if self.posting_as_flag==0:
            self.center_posting_as_button.config(text="Posting As: Right")
            self.posting_as_flag=1
        else:
            self.center_posting_as_button.config(text="Posting As: Left")
            self.posting_as_flag=0
        
    def sub_mode_toggle(self):
        if self.sub_mode_flag.get()==1: #TURNING ON SUB MODE
            if self.transfer_from_arrow == 0: #From left
                self.b_button_pull_saves.config(text="Select Sub")
                self.b_button_pull_saves.config(command=self.b_set_sub)
                self.b_clear_canvas()
                self.b_canvas_label.config(text="{}'s Subreddit: {}".format(self.b_username,self.b_target_sub))

                self.button_pull_saves.config(text="Pull Saves")
                self.button_pull_saves.config(command=self.pull_saves)
                self.canvas_label.config(text=f"{self.username}'s Saved List")

            else:
                self.button_pull_saves.config(text="Select Sub")
                self.button_pull_saves.config(command=self.set_sub)
                self.clear_canvas()
                self.canvas_label.config(text="{}'s Subreddit: {}".format(self.username,self.self.target_sub))

                self.b_button_pull_saves.config(text="Pull Saves")
                self.b_button_pull_saves.config(command=self.b_pull_saves)
                self.b_canvas_label.config(text=f"{self.b_username}'s Saved List")

            self.center_button_save.config(text="Post")
            self.center_button_save.config(command=self.make_post)
            self.center_button_transfer.grid_forget()
            self.center_posting_as_button.grid(row=0,column=1,padx=(3,3))

            
        
        else: #TURNING OFF SUB MODE
            #if self.transfer_from_arrow == 0: #If arrow goes left to right, reset right
            self.b_button_pull_saves.config(text="Pull Saves")
            self.b_button_pull_saves.config(command=self.b_pull_saves)

            self.b_canvas_label.config(text=f"{self.b_username}'s Saved List")

            self.button_pull_saves.config(text="Pull Saves")
            self.button_pull_saves.config(command=self.pull_saves)

            self.canvas_label.config(text=f"{self.username}'s Saved List")

            self.center_button_save.config(text="UnSave")
            self.center_button_save.config(command=self.unsave_center_post)
            self.center_posting_as_button.grid_forget()
            self.center_button_transfer.grid(row=0,column=1,padx=(3,3))
        
    def build_middle(self):
        self.built_middle=1

        for i in range(0,3):
            self.main_frame.grid_columnconfigure(i,weight=1)

        if self.right_logged_in == 0:
            self.b_entry_frame.grid(row=0,column=2)

        
        self.mid_column_frame = ttk.Frame(self.main_frame)
        self.mid_column_frame.grid(row=0,column=1,sticky='n'+'s')
        self.mid_column_frame.bind('<B1-Motion>',self.move_window)
        self.mid_column_frame.bind('<Button-1>',self.get_pos)
        for i in range(0,7):
            self.mid_column_frame.grid_rowconfigure(i,weight=1)

        self.mid_column_frame.grid_columnconfigure(0,weight=1)


        self.mid_label_frame = ttk.Frame(self.mid_column_frame)
        self.mid_label_frame.grid(row=0,column=0)
        self.label_transfer = ttk.Label(self.mid_label_frame,text="TRANSFER DIRECTION",font=("TkDefaultFont",9,'bold'))
        self.label_transfer.pack()
        self.canvas_transfer = tk.Canvas(self.mid_label_frame,bg='#33393b',width=90,height=80,highlightthickness=0)
        self.canvas_transfer.pack()
        
        self.canvas_transfer.bind("<Button-1>",self.flip_arrow)
        self.canvas_transfer.create_line(0,20,90,20,arrow='last',width=7,fill='black')
        self.canvas_transfer.create_line(0,50,90,50,arrow='last',width=7,fill='black')
        self.mid_control_box = ttk.Frame(self.mid_column_frame)
        self.mid_control_box.grid(row=1,column=0)

        self.manual_flag = tk.IntVar()
        self.unsave_after_transfer_flag =tk.IntVar()
        self.automatic_flag = tk.IntVar()
        self.delete_after_transfer_flag = tk.IntVar()
        self.video_flag = tk.IntVar()
        self.vlc_video_flag = tk.IntVar()
        self.sub_mode_flag = tk.IntVar()

        self.check_video = ttk.Checkbutton(self.mid_control_box,var=self.video_flag,text="Video Player (Python-MPV)",command=self.enable_disable_player)
        self.check_video.grid(row=0,column=0,columnspan=2)
        self.check_vlc = ttk.Checkbutton(self.mid_control_box,var=self.vlc_video_flag,text="Video Player (VLC)",command=self.vlc_enable_disable_player) #disable player, run vlc enable_disable_player
        self.check_vlc.grid(row=1,column=0,columnspan=2)
        self.check_sub_mode = ttk.Checkbutton(self.mid_control_box,var=self.sub_mode_flag,text="Transfer to Subreddit",command=self.sub_mode_toggle)
        self.check_sub_mode.grid(row=2,column=0,columnspan=2)
        self.check_unsave_after_transfer = ttk.Checkbutton(self.mid_control_box,var=self.unsave_after_transfer_flag,text="Unsave After Transfer")
        self.check_unsave_after_transfer.grid(row=3,column=0,columnspan=2)
        
        #Haven't (and idk if I want to) allowed Transfering from sub to sub yet

        
        self.manual_flag.set(1)
        self.unsave_after_transfer_flag.set(1)
        #TODO: Automatic function operates based on the top widget on the "from" side, so it breaks if you don't remove the widgets (by unsaving), could add current_index instead or something
        self.check_unsave_after_transfer.config(state='disabled')


        self.placeholder_card = ttk.Frame(self.mid_column_frame)
        self.placeholder_card.grid(row=2,column=0)

        img = Image.open('{}/placeholder.jpg'.format(self.cwd))
        photo = ImageTk.PhotoImage(img)
        self.placeholder_image=(photo)

        self.placeholder_button = ttk.Button(self.placeholder_card,image=photo,command=self.play_video)
        self.placeholder_button.grid(row=0,column=0,rowspan=3)
        self.placeholder_title=ttk.Label(self.placeholder_card,text="Title")
        self.placeholder_title.grid(row=0,column=1,sticky='w')

        self.placeholder_sub=ttk.Label(self.placeholder_card,text="Subreddit")
        self.placeholder_sub.grid(row=1,column=1,sticky='w')

        self.placeholder_link=ttk.Label(self.placeholder_card,text="Hotlink..")
        self.placeholder_link.grid(row=2,column=1,sticky='w')

        self.center_buttons = ttk.Frame(self.mid_column_frame)
        self.center_buttons.grid(row=4,column=0)
        
        self.center_button_save = ttk.Button(self.center_buttons,text="UnSave",width=7,command=self.unsave_center_post)
        self.center_button_save.grid(row=0,column=0,padx=(0,3))
        self.center_button_transfer = ttk.Button(self.center_buttons,text="Transfer",width=7,command=self.transfer_post)
        self.center_button_transfer.grid(row=0,column=1,padx=(3,3))
        self.center_button_hide = ttk.Button(self.center_buttons,text="Hide",width=7,command=self.hide_post)
        self.center_button_hide.grid(row=0,column=2,padx=(3,0))


        self.center_start_button = ttk.Button(self.mid_column_frame,text="Start",width=15,command=self.start_loop)
        self.center_start_button.grid(row=5,column=0)

        self.center_posting_as_button = ttk.Button(self.center_buttons,text="Posting As: Left",command=self.posting_as_toggle)
        
        self.progress_bar_frame = ttk.Frame(self.mid_column_frame)
        self.progress_bar_frame.grid(row=6,column=0)
        self.progress_bar = ttk.Progressbar(self.progress_bar_frame,orient='horizontal',length=100,mode='determinate')
        self.b_progress_bar = ttk.Progressbar(self.progress_bar_frame,orient='horizontal',length=100,mode='determinate')


        ###VIDEO PLAYER###
       
    def mpv_scroll_handler(self,event):
        #print(event)
        if event.delta > 0:
            self.zoom_level+=2
            self.current_new_button_width+=6
            self.current_new_button_height+=2
            self.current_new_button_xpos -=21
            self.current_new_button_ypos-=20
            self.video_button.config(width=self.current_new_button_width,height=self.current_new_button_height)
            self.video_button.place(x=self.current_new_button_xpos,y=self.current_new_button_ypos)
        else:
            self.zoom_level-=2
            self.current_new_button_width-=6
            self.current_new_button_height-=2
            self.current_new_button_xpos +=21
            self.current_new_button_ypos+=20
            self.video_button.config(width=self.current_new_button_width,height=self.current_new_button_height)
            self.video_button.place(x=self.current_new_button_xpos,y=self.current_new_button_ypos)

        #if 'MouseWheel' in str(event):
        #    if event.delta > 0:
        #        self.player.keypress('0')
        #    else:
        #        self.player.keypress('9')
        #else:
        #    self.player.keypress('.')
    def reset_zoom(self,event):
        self.video_button.config(width=38,height=9)
        self.video_button.place(x=348,y=340)
        self.zoom_level=0
    def enable_disable_player(self):
        self.current_new_button_width=38
        self.current_new_button_height=9
        self.current_new_button_xpos = 348
        self.current_new_button_ypos = 340

        if self.video_flag.get()==0:
            self.player.terminate()
            self.fake_video_player_frame.destroy()
            self.video_button.destroy()
            self.check_vlc.config(state='enabled')

        else: #Turned On
            self.check_vlc.config(state='disabled')
            self.fake_video_player_frame = ttk.Frame(self.mid_column_frame)
            self.fake_video_player_frame.grid(row=3,column=0)
            self.fake_video_button = tk.Button(self.fake_video_player_frame,bg='#33393b',bd=0,highlightthickness=0,width=38,height=9)
            self.fake_video_button.pack()

            #self.video_button.bind("<Button-3>",self.fullscreen_maybe)
            
            self.video_button=tk.Button(self.root,width=38,height=9,bg='#33393b',command=lambda:self.player.keypress('p'))
            self.video_button.place(x=348,y=340)
            self.video_button.bind("<MouseWheel>", self.mpv_scroll_handler)
            self.video_button.bind("<Button-3>",self.reset_zoom)
            self.player=mpv.MPV(ytdl=True,ytdl_format="best",background='#33393b',volume=0,input_default_bindings=True,input_vo_keyboard=True,wid=str(int(self.video_button.winfo_id())))
            self.player.loop_playlist='inf'

    
    def vlc_enable_disable_player(self):

        if self.vlc_video_flag.get()==0:
            self.player.stop()
            self.fake_video_player_frame.destroy()
            self.check_video.config(state='enabled')
            #self.video_button.destroy()
            #print("Off")
        else: #Turned Off
            #print("On")
            
            self.check_video.config(state='disabled')
            
            self.vlc_instance = vlc.Instance('--verbose 0')
            
            self.fake_video_player_frame = ttk.Frame(self.mid_column_frame)
            self.fake_video_player_frame.grid(row=3,column=0)
            self.fake_video_button = tk.Button(self.fake_video_player_frame,bg='#33393b',width=38,height=9,command=lambda:print("Clicked Video Player"))
            self.fake_video_button.pack()

            
            self.video_player_button_frame = ttk.Frame(self.fake_video_player_frame)
            self.video_player_button_frame.pack(pady=(1,0))
            self.video_player_resume_button = ttk.Button(self.video_player_button_frame,text="Play/Pause",command=lambda:self.player.pause())
            self.video_player_resume_button.grid(row=0,column=0)
            #self.video_button=tk.Button(self.root,width=38,height=9)
            #self.video_button.place(x=348,y=329)
            self.player = self.vlc_instance.media_player_new()
            self.player.set_hwnd(self.fake_video_button.winfo_id())


    def play_video(self):
        if(self.vlc_video_flag.get()==1):
            self.vlc_play_video()
            return

        if self.video_flag.get()==1:

            full_link = self.cc_inner_url
            if self.nsfw_flag.get()==1:
                full_link=self.cc_inner_url.replace('gfycat.com','redgifs.com/watch')
            
            ytdl_options = {
            'playlistend':1,
            'quiet':True
            }

            with youtube_dl.YoutubeDL(ytdl_options) as ytdl:
                info_dict = ytdl.extract_info(full_link,download=False)
                try:
                    new_link=info_dict['url']
                except KeyError:
                    new_link=info_dict['entries'][0]['url']

            self.player.play(full_link)
    
    def vlc_link_converter(self,link):
        ytdl_options = {
            'playlistend':1,
            'quiet':True
        }
        if self.nsfw_flag.get()==1 or self.b_nsfw_flag.get()==1:
            new_link=link.replace('gfycat.com','redgifs.com/watch')

        if 'imgur' in link:
            new_link = link.replace('gifv','mp4')
        else:
            print("Before ytdl: ",new_link)
            with youtube_dl.YoutubeDL(ytdl_options) as ytdl:
                info_dict = ytdl.extract_info(link,download=False)
                print(info_dict)
                try:
                    new_link=info_dict['url']
                except KeyError:
                    new_link=info_dict['entries'][0]['url']

        print(new_link)
        return new_link.replace('.gif','.mp4').replace('.gifv','.mp4')

    def vlc_play_video(self):
        #print("here")
        if self.vlc_video_flag.get()==1:
            #if self.nsfw_flag.get()==1
            
            #if self.nsfw_flag.get()==1:
            #    full_link=self.cc_inner_url.replace('gfycat.com','redgifs.com/watch')
            #    full_link=self.link_converter(full_link)
            full_link=self.vlc_link_converter(self.cc_inner_url)

            print("VLC PLAYING: ",full_link)
            self.player.set_mrl(full_link)
            self.player.play()
            print("Should be playing")
            #print(full_link)


    def change_page(self,pagenum):
        
        self.page_offset = int(pagenum)*100
        print("page change to ",pagenum,"offset: ",self.page_offset)
        self.canvas_label.config(text="{}'s Saved List - {} Posts Found - Page {}".format(self.username,len(self.filtered_list),pagenum))
        t1 = threading.Thread(target=self.display_saved)
        t1.daemon=True
        t1.start()
    
    def b_change_page(self,pagenum):
        
        self.b_page_offset = int(pagenum)*100
        print("page change to ",pagenum,"offset: ",self.b_page_offset)
        self.b_canvas_label.config(text="{}'s Saved List - {} Posts Found - Page {}".format(self.b_username,len(self.b_filtered_list),pagenum))
        t1 = threading.Thread(target=self.b_display_saved)
        t1.daemon=True
        t1.start()
        #So far don't need to do anything to kill other running threads as they crash anyways. But functionality based on crashing is probably not good so maybe I'll come back to this

        
        

    def build_feed(self):
        self.left_logged_in=1
        self.user_object = self.r.user.me()
        self.entry_frame.destroy()
        self.left_column_frame= ttk.Frame(self.main_frame)
        self.left_column_frame.grid(row=0,column=0,sticky='nw')

        self.left_column_frame.bind('<B1-Motion>',self.move_window)
        self.left_column_frame.bind('<Button-1>',self.get_pos)

        self.login_card = ttk.Frame(self.left_column_frame,takefocus=False)
        self.login_card.pack(fill=tk.X,pady=5)

        for i in range(0,2):
            self.login_card.grid_rowconfigure(i,weight=1)

        self.reverse_flag =tk.IntVar()
        self.nsfw_flag = tk.IntVar()
        self.sfw_flag= tk.IntVar()
        self.text_post_flag= tk.IntVar()
        self.thumbnail_flag = tk.IntVar()
        self.sub_flag=tk.IntVar()
        self.top_flag = tk.IntVar()
        self.hot_flag = tk.IntVar()
        self.new_flag= tk.IntVar()

        self.sfw_flag.set(1)
        self.thumbnail_flag.set(1)
        self.top_flag.set(1)

        self.label_top = ttk.Label(self.login_card,text="Logged in as: {}".format(self.username),font=("TkDefaultFont",9,'bold')) #.format(self.user_object.name)
        self.label_top.grid(row=0,column=0,padx=5,pady=5)
        self.button_pull_saves = ttk.Button(self.login_card,text="Pull Saves",command=self.pull_saves)
        self.button_pull_saves.grid(row=2,column=1,padx=5,pady=5)
        self.user_thumb = ttk.Button(self.login_card,text="Thumb")
        self.user_thumb.grid(row=0,column=1,rowspan=2,columnspan=2)

        thumb_url = self.user_object.icon_img
        
        try:
            urllib.request.urlretrieve(thumb_url,'{}/thumbs/user_icon.jpg'.format(self.cwd))
        except:
            print("Urllib error")

        
        img = Image.open('{}/thumbs/user_icon.jpg'.format(self.cwd))
        img.thumbnail((50,50))
        photo = ImageTk.PhotoImage(img)
        self.user_icons[0]=photo
        self.user_thumb.config(image=photo)


        self.button_pull_sub = ttk.Button(self.login_card,text="Pull Subreddit",command=self.pull_from_subreddit)
        self.button_pull_sub.grid(row=1,column=0,padx=5,pady=5)
        self.entry_pull_sub = ttk.Combobox(self.login_card,values=self.left_sub_list,width=20)
        self.entry_pull_sub.grid(row=2,column=0,padx=5,pady=5)
        self.button_load_saves = ttk.Button(self.login_card,text="Extract List",command=self.extract_save_file)
        self.button_load_saves.grid(row=2,column=2)

        
        self.feed_frame= ttk.Frame(self.left_column_frame)
        self.feed_frame.grid_rowconfigure(0,weight=1)
        self.feed_frame.grid_columnconfigure(0,weight=1)
        self.feed_frame.grid_propagate(False)
        self.feed_frame.pack(expand=True,fill='y')

        #Build Scrollable Feed
        self.canvas_label = ttk.Label(self.feed_frame,text=f"{self.username}'s Saved List")
        self.canvas_label.pack(pady=1,fill='x')

        self.canvas = tk.Canvas(self.feed_frame,bg='black',width=320,height=340,highlightthickness=0) #550
        self.canvas.pack(padx=2,expand=True,fill='both')

        self.ybar=ttk.Scrollbar(self.feed_frame,orient="vertical",command=self.canvas.yview)
        self.ybar.grid(column=1,row=0,sticky='ns')

        self.canvas.configure(yscrollcommand=self.ybar.set)

        self.frame_thumbs=ttk.Frame(self.canvas)
        self.canvas.create_window((0,0),window=self.frame_thumbs,anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.root.bind_all("<MouseWheel>",self.on_mousewheel)
        self.root.bind_all("<Button-3>",self.on_rightclick)
        self.canvas.yview_moveto('0')

        #Build Scrollable Feed

        self.page_bar = ttk.Frame(self.left_column_frame)
        self.page_bar.pack(pady=3)

        for i in range(0,10):
            self.page_bar.grid_columnconfigure(i,weight=1)
        
        #Pagination
        for i in range(0,9):
            button = ttk.Button(self.page_bar,command=lambda a=i:self.change_page(a),text=i+1,width=1)
            button.grid(row=0,column=i,padx=5.2)
        
        

        self.end_card = ttk.Frame(self.left_column_frame,takefocus=False)
        self.end_card.pack(side='bottom')
        
        self.check_nsfw = ttk.Checkbutton(self.end_card,text="NSFW Posts",variable=self.nsfw_flag)
        self.check_nsfw.grid(row=0,column=0)
        self.check_sfw = ttk.Checkbutton(self.end_card,text="SFW Posts",variable=self.sfw_flag)
        self.check_sfw.grid(row=1,column=0)
        self.check_text = ttk.Checkbutton(self.end_card,text="Text Posts",variable=self.text_post_flag)
        self.check_text.grid(row=2,column=0)
        
        self.check_reverse = ttk.Checkbutton(self.end_card,text="Reverse List",variable=self.reverse_flag,offvalue=0)
        self.check_reverse.grid(row=0,column=1)
        self.check_thumbnails= ttk.Checkbutton(self.end_card,text="Thumbnails",variable=self.thumbnail_flag)
        self.check_thumbnails.grid(row=1,column=1)
        self.check_sub = ttk.Checkbutton(self.end_card,text="Specific Subs",variable=self.sub_flag)
        self.check_sub.grid(row=2,column=1)

        self.check_top = ttk.Checkbutton(self.end_card,text="Top (Subreddit)",variable=self.top_flag)
        self.check_top.grid(row=0,column=2)
        self.check_hot = ttk.Checkbutton(self.end_card,text="Hot (Subreddit)",variable=self.hot_flag)
        self.check_hot.grid(row=1,column=2)
        self.check_new = ttk.Checkbutton(self.end_card,text="New (Subreddit)",variable=self.new_flag)
        self.check_new.grid(row=2,column=2)

        self.button_refresh=ttk.Button(self.end_card,text="Refresh",width=20,command=self.refresh_filters)
        self.button_refresh.grid(row=3,column=0,columnspan=3,padx=5,pady=5)

        if self.built_middle == 0:
            self.build_middle()

    
    def b_build_feed(self):
        self.right_logged_in=1
        self.b_user_object = self.r2.user.me()
        self.b_entry_frame.destroy()
        self.right_column_frame= ttk.Frame(self.main_frame)
        self.right_column_frame.grid(row=0,column=2,sticky='ne')

        self.right_column_frame.bind('<B1-Motion>',self.move_window)
        self.right_column_frame.bind('<Button-1>',self.get_pos)

        self.b_login_card = ttk.Frame(self.right_column_frame,takefocus=False)
        self.b_login_card.pack(fill=tk.X,pady=5)

        for i in range(0,2):
            self.b_login_card.grid_rowconfigure(i,weight=1)

        self.b_reverse_flag=tk.IntVar()
        self.b_nsfw_flag = tk.IntVar()
        self.b_sfw_flag= tk.IntVar()
        self.b_text_post_flag= tk.IntVar()
        self.b_thumbnail_flag = tk.IntVar()
        self.b_sub_flag=tk.IntVar()
        self.b_sub_flag=tk.IntVar()
        self.b_top_flag = tk.IntVar()
        self.b_hot_flag = tk.IntVar()
        self.b_new_flag= tk.IntVar()

        self.b_sfw_flag.set(1)
        self.b_thumbnail_flag.set(1)
        self.b_top_flag.set(1)

        self.b_label_top = ttk.Label(self.b_login_card,text="Logged in as: {}".format(self.b_username),font=("TkDefaultFont",9,'bold')) #.format(self.user_object.name)
        self.b_label_top.grid(row=0,column=0,padx=5,pady=5)
        self.b_button_pull_saves = ttk.Button(self.b_login_card,text="Pull Saves",command=self.b_pull_saves)
        self.b_button_pull_saves.grid(row=2,column=1,padx=5,pady=5)
        self.b_user_thumb = ttk.Button(self.b_login_card,text="Thumb")
        self.b_user_thumb.grid(row=0,column=1,rowspan=2,columnspan=2)

        thumb_url = self.b_user_object.icon_img
        
        try:
            urllib.request.urlretrieve(thumb_url,'{}/thumbs/user_icon.jpg'.format(self.cwd))
        except:
            print("Urllib error")
            print(thumb_url)
        
        img = Image.open('{}/thumbs/user_icon.jpg'.format(self.cwd))
        img.thumbnail((50,50))
        photo = ImageTk.PhotoImage(img)
        self.user_icons[1]=photo
        self.b_user_thumb.config(image=photo)

        self.b_button_pull_sub = ttk.Button(self.b_login_card,text="Pull Subreddit",command=self.b_pull_from_subreddit)
        self.b_button_pull_sub.grid(row=1,column=0,padx=5,pady=5)
        self.b_entry_pull_sub = ttk.Combobox(self.b_login_card,values=self.right_sub_list,width=20)
        self.b_entry_pull_sub.grid(row=2,column=0,padx=5,pady=5)
        self.b_extract_saves = ttk.Button(self.b_login_card,text="Extract List", command =self.b_extract_save_file)
        self.b_extract_saves.grid(row=2,column=2)


        
        self.b_feed_frame= ttk.Frame(self.right_column_frame)
        self.b_feed_frame.grid_rowconfigure(0,weight=1)
        self.b_feed_frame.grid_columnconfigure(0,weight=1)
        self.b_feed_frame.grid_propagate(False)
        self.b_feed_frame.pack(expand=True,fill='y')


        #Build Scrollable Feed
        self.b_canvas_label = ttk.Label(self.b_feed_frame,text=f"{self.b_username}'s Saved List")
        self.b_canvas_label.pack(pady=1,fill='x')
        self.b_canvas = tk.Canvas(self.b_feed_frame,bg='black',width=320,height=340,highlightthickness=0) #550
        self.b_canvas.pack(padx=2,expand=True,fill='both')

        self.b_ybar=ttk.Scrollbar(self.b_feed_frame,orient="vertical",command=self.b_canvas.yview)
        self.b_ybar.grid(column=1,row=0,sticky='ns')
        self.b_canvas.configure(yscrollcommand=self.b_ybar.set)

        self.b_frame_thumbs=ttk.Frame(self.b_canvas)
        self.b_canvas.create_window((0,0),window=self.b_frame_thumbs,anchor='nw')
        self.b_canvas.config(scrollregion=self.b_canvas.bbox('all'))
        self.b_canvas.yview_moveto('0')

        #Build Scrollable Feed

        self.b_page_bar = ttk.Frame(self.right_column_frame)
        self.b_page_bar.pack(pady=3)

        for i in range(0,10):
            self.b_page_bar.grid_columnconfigure(i,weight=1)
        
        #Pagination
        for i in range(0,9):
            button = ttk.Button(self.b_page_bar,command=lambda a=i:self.b_change_page(a),text=i+1,width=1)
            button.grid(row=0,column=i,padx=5.2)

        self.b_end_card = ttk.Frame(self.right_column_frame,takefocus=False)
        self.b_end_card.pack(side='bottom')
        
        self.b_check_nsfw = ttk.Checkbutton(self.b_end_card,text="NSFW Posts",variable=self.b_nsfw_flag)
        self.b_check_nsfw.grid(row=0,column=0)
        self.b_check_sfw = ttk.Checkbutton(self.b_end_card,text="SFW Posts",variable=self.b_sfw_flag)
        self.b_check_sfw.grid(row=1,column=0)
        self.b_check_text = ttk.Checkbutton(self.b_end_card,text="Text Posts",variable=self.b_text_post_flag)
        self.b_check_text.grid(row=2,column=0)
        
        self.b_check_reverse = ttk.Checkbutton(self.b_end_card,text="Reverse List",variable=self.b_reverse_flag)
        self.b_check_reverse.grid(row=0,column=1)
        self.b_check_thumbnails= ttk.Checkbutton(self.b_end_card,text="Thumbnails",variable=self.b_thumbnail_flag)
        self.b_check_thumbnails.grid(row=1,column=1)
        self.b_check_sub = ttk.Checkbutton(self.b_end_card,text="Specific Subs",variable=self.b_sub_flag)
        self.b_check_sub.grid(row=2,column=1)

        self.b_check_top = ttk.Checkbutton(self.b_end_card,text="Top (Subreddit)",variable=self.b_top_flag)
        self.b_check_top.grid(row=0,column=2)
        self.b_check_hot = ttk.Checkbutton(self.b_end_card,text="Hot (Subreddit)",variable=self.b_hot_flag)
        self.b_check_hot.grid(row=1,column=2)
        self.b_check_new = ttk.Checkbutton(self.b_end_card,text="New (Subreddit)",variable=self.b_new_flag)
        self.b_check_new.grid(row=2,column=2)

        
        self.b_button_refresh=ttk.Button(self.b_end_card,text="Refresh",width=20,command=self.b_refresh_filters)
        self.b_button_refresh.grid(row=3,column=0,columnspan=3,padx=5,pady=5)

        if self.built_middle == 0:
            self.build_middle()

    
    

    def login(self,left_right):
        if left_right == 0:
            self.username = self.entry_user.get()
            self.password = self.entry_pass.get()
            self.client_id = self.entry_client_id.get()
            self.client_secret = self.entry_client_secret.get()
            self.user_agent = self.entry_user_agent.get()

            self.r = praw.Reddit(client_id=self.client_id,
                            client_secret=self.client_secret,
                            password=self.password,
                            user_agent=self.user_agent,
                            username=self.username)


            self.build_feed()
        else:
            self.b_username = self.b_entry_user.get()
            self.b_password = self.b_entry_pass.get()
            self.b_client_id = self.b_entry_client_id.get()
            self.b_client_secret = self.b_entry_client_secret.get()
            self.b_user_agent = self.b_entry_user_agent.get()


            self.r2 = praw.Reddit(client_id=self.b_client_id,
                            client_secret=self.b_client_secret,
                            password=self.b_password,
                            user_agent=self.b_user_agent,
                            username=self.b_username)

            self.b_build_feed()
        
        
    
    def clear_fields(self,left_or_right):
        if left_or_right==0: #0 = left
            self.entry_user.delete(0,tk.END)
            self.entry_pass.delete(0,tk.END)
            self.entry_client_id.delete(0,tk.END)
            self.entry_client_secret.delete(0,tk.END)
            self.entry_user_agent.delete(0,tk.END)
        else:
            self.b_entry_user.delete(0,tk.END)
            self.b_entry_pass.delete(0,tk.END)
            self.b_entry_client_id.delete(0,tk.END)
            self.b_entry_client_secret.delete(0,tk.END)
            self.b_entry_user_agent.delete(0,tk.END)

    def load_saved(self,left_or_right):
        if(os.path.exists('login.txt')):  #If login already exists
            with open('login.txt') as file:
                lines = file.readlines()
                if left_or_right==0: # 0 = left
                    self.clear_fields(0)
                    self.entry_user.insert(0,lines[self.login_index+0].split('=')[1].strip('\n'))
                    self.entry_pass.insert(0,lines[self.login_index+1].split('=')[1].strip('\n'))
                    self.entry_client_id.insert(0,lines[self.login_index+2].split('=')[1].strip('\n'))
                    self.entry_client_secret.insert(0,lines[self.login_index+3].split('=')[1].strip('\n'))
                    self.entry_user_agent.insert(0,lines[self.login_index+4].split('=')[1].strip('\n'))
                    self.login_index+=6
                    if self.login_index > len(lines):
                        self.login_index=0
                else:
                    self.clear_fields(1)
                    self.b_entry_user.insert(0,lines[self.login_index+0].split('=')[1].strip('\n'))
                    self.b_entry_pass.insert(0,lines[self.login_index+1].split('=')[1].strip('\n'))
                    self.b_entry_client_id.insert(0,lines[self.login_index+2].split('=')[1].strip('\n'))
                    self.b_entry_client_secret.insert(0,lines[self.login_index+3].split('=')[1].strip('\n'))
                    self.b_entry_user_agent.insert(0,lines[self.login_index+4].split('=')[1].strip('\n'))
                    self.login_index+=6
                    if self.login_index > len(lines):
                        self.login_index=0


    def build_login_page(self):
        
        self.entry_frame = ttk.Frame(self.main_frame)
        self.entry_frame.grid(row=0,column=0)

        self.b_entry_frame = ttk.Frame(self.main_frame)
        self.b_entry_frame.grid(row=0,column=1)
        
        for i in range(0,2):
            self.entry_frame.grid_columnconfigure(i,weight=1)
            self.b_entry_frame.grid_columnconfigure(i,weight=1)

        for i in range(0,5):
            self.entry_frame.grid_rowconfigure(i,weight=1)
            self.b_entry_frame.grid_rowconfigure(i,weight=1)

        self.label_user = ttk.Label(self.entry_frame,text=" Username:")
        self.label_user.grid(row=0,column=0)
        self.entry_user = ttk.Entry(self.entry_frame,show="*")
        self.entry_user.grid(row=0,column=1)

        self.b_label_user = ttk.Label(self.b_entry_frame,text=" Username:")
        self.b_label_user.grid(row=0,column=0)
        self.b_entry_user = ttk.Entry(self.b_entry_frame,show="*")
        self.b_entry_user.grid(row=0,column=1)


        self.label_pass = ttk.Label(self.entry_frame,text="Password:")
        self.label_pass.grid(row=1,column=0)
        self.entry_pass = ttk.Entry(self.entry_frame,show="*")
        self.entry_pass.grid(row=1,column=1)

        self.b_label_pass = ttk.Label(self.b_entry_frame,text="Password:")
        self.b_label_pass.grid(row=1,column=0)
        self.b_entry_pass = ttk.Entry(self.b_entry_frame,show="*")
        self.b_entry_pass.grid(row=1,column=1)


        self.label_client_id = ttk.Label(self.entry_frame,text="Client ID:")
        self.label_client_id.grid(row=2,column=0)
        self.entry_client_id = ttk.Entry(self.entry_frame)
        self.entry_client_id.grid(row=2,column=1)

        self.b_label_client_id = ttk.Label(self.b_entry_frame,text="Client ID:")
        self.b_label_client_id.grid(row=2,column=0)
        self.b_entry_client_id = ttk.Entry(self.b_entry_frame)
        self.b_entry_client_id.grid(row=2,column=1)


        self.label_client_secret = ttk.Label(self.entry_frame,text="Client Secret")
        self.label_client_secret.grid(row=3,column=0)
        self.entry_client_secret = ttk.Entry(self.entry_frame)
        self.entry_client_secret.grid(row=3,column=1)

        self.b_label_client_secret = ttk.Label(self.b_entry_frame,text="Client Secret")
        self.b_label_client_secret.grid(row=3,column=0)
        self.b_entry_client_secret = ttk.Entry(self.b_entry_frame)
        self.b_entry_client_secret.grid(row=3,column=1)


        self.label_user_agent = ttk.Label(self.entry_frame,text="User Agent")
        self.label_user_agent.grid(row=4,column=0)
        self.entry_user_agent = ttk.Entry(self.entry_frame)
        self.entry_user_agent.grid(row=4,column=1)

        self.b_label_user_agent = ttk.Label(self.b_entry_frame,text="User Agent")
        self.b_label_user_agent.grid(row=4,column=0)
        self.b_entry_user_agent = ttk.Entry(self.b_entry_frame)
        self.b_entry_user_agent.grid(row=4,column=1)

        self.load_login = ttk.Button(self.entry_frame,text="Cycle Logins",command=lambda a=0: self.load_saved(a))
        self.load_login.grid(row=5,column=1)
        self.b_load_login = ttk.Button(self.b_entry_frame,text="Cycle Logins",command=lambda a=1: self.load_saved(a))
        self.b_load_login.grid(row=5,column=1)

        self.login_button = ttk.Button(self.entry_frame,width=10,text="Login",command=lambda a=0: self.login(a))
        self.login_button.grid(row=5,column=0,columnspan=1,pady=4)
        self.b_login_button = ttk.Button(self.b_entry_frame,width=10,text="Login",command=lambda a=1: self.login(a))
        self.b_login_button.grid(row=5,column=0,columnspan=1,pady=4)



    def update(self):
        #for thread in threading.enumerate(): 
        #    print(thread.name)
        
        if self.left_logged_in==1:
            self.canvas.config(scrollregion=self.canvas.bbox('all'))
        
        if self.right_logged_in==1:
            self.b_canvas.config(scrollregion=self.b_canvas.bbox('all'))

        if self.generation_flag==1:
            try:

                self.button_refresh.config(text="Stop Generation")
                self.button_refresh.config(command=lambda a=0: self.stop_generation(a))
                self.button_pull_saves.config(state='disabled')
                self.button_pull_sub.config(state='disabled')
            except:
                pass
        else:
            try:
                self.button_refresh.config(text="Refresh")
                self.button_refresh.config(command=self.refresh_filters)
                self.button_pull_saves.config(state='normal')
                self.button_pull_sub.config(state='normal')
            except:
                pass
        if self.b_generation_flag == 1:
            try:
                self.b_button_refresh.config(text="Stop Generation")
                self.b_button_refresh.config(command=lambda a=1: self.stop_generation(a))
                self.b_button_pull_saves.config(state='disabled')
                self.b_button_pull_sub.config(state='disabled')
            except:
                pass
        else:
            try:
                self.b_button_refresh.config(text="Refresh")
                self.b_button_refresh.config(command=self.b_refresh_filters)
                self.b_button_pull_saves.config(state='normal')
                self.b_button_pull_sub.config(state='normal')
            except:
                pass

        if self.loop_it==1:
            self.posted_count+=1
            print(self.posted_count)
            self.automatic_func(self.current_center_acc)
        else:
            self.posted_count=0

        self.root.after(500,self.update)
    def get_pos(self,event):
        xwin = self.root.winfo_x()
        ywin = self.root.winfo_y()
        startx = event.x_root
        starty = event.y_root

        self.ywin = ywin - starty
        self.xwin = xwin - startx

    def move_window(self,event):
        self.root.geometry('+{0}+{1}'.format(event.x_root+self.xwin,event.y_root+self.ywin))


    def create_window(self):
        self.root = tk.Tk()
        self.root.tk.eval("""
set base_theme_dir ./awthemes-10.4.0/

package ifneeded awthemes 10.4.0 \
    [list source [file join $base_theme_dir awthemes.tcl]]
package ifneeded awdark 7.12 \
    [list source [file join $base_theme_dir awdark.tcl]]
""")
        self.root.tk.call("package","require",'awdark')
        
        ttk.Style().theme_use('awdark')
        #s = ttk.Style()
        #ttk.Style().configure('testStyle.TFrame',background='#fffffff') #33393b
        
        self.root.title("Reddit Saved Transferer - https://github.com/DeeFrancois")
        self.root.geometry("984x610")
        self.root.resizable(False,False)
        self.root.bind('<Escape>',self.close)
        #self.root.overrideredirect(1)
        #self.root.attributes('-topmost',1)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both',expand=True)
        self.main_frame.grid_rowconfigure(0,weight=1)
        for i in range(0,2):
            self.main_frame.grid_columnconfigure(i,weight=1)

        self.build_login_page()
        
        self.main_frame.bind('<B1-Motion>',self.move_window)
        self.main_frame.bind('<Button-1>',self.get_pos)

        self.root.after(100,self.update)
        self.root.mainloop()

def main():
    run = reddit_saved()
    run.create_window()

main()