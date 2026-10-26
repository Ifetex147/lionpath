"""
LionPath Campus Assistant - Official Ground-Truth Seed Script
Faculty of Physical Sciences, University of Nigeria, Nsukka (UNN)

Populates authentic:
1. Campus Landmarks & Lecture Venues (Carver, NAL Library, Student Affairs, Abuja Building, SLT, NCSB, Bello, VC Office, Gates, Hostels, etc.)
2. Real Walkway Graph with Ground-Truth Pedestrian Timings & Visual Turn Directions
3. 10 Comprehensive Freshman Onboarding Guides (JAMB, Faculty Clearance at Carver, Dept Reg, NAL Library, CBT, ID Card, GS, Clionet Wi-Fi, Medicals, Hostel Booting)
4. Official UNN Faculty Events (Faculty Orientation, Matriculation, Dept Meetings)
5. Complete 100L First-Semester Timetables for all 8 Academic Tracks (CS, CS & Stats, Stats, Geology, SLT, Maths, Physics & Astronomy, Pure & Industrial Chemistry)
"""

from app import app
from models import db, Node, Edge, OrientationKB, Timetable, Event

def seed_database():
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()

        # 1. CAMPUS LANDMARKS & BUILDINGS (NODES)
        nodes = {
            "carver": Node(
                formal_name="Carver Building",
                informal_names="faculty,faculty building,carver,carver building,carver block,green and white building,building opposite student affairs,physical sciences faculty building,faculty general office,clearance office,physics lecture hall,chemistry lecture hall",
                category="building",
                description="Green and white building opposite Student Affairs and hostels row; Faculty of Physical Sciences building housing the Faculty General Office for clearance.",
                photo_path="carver_building.jpeg"
            ),
            "na_lib": Node(
                formal_name="Nnamdi Azikiwe Library (NAL)",
                informal_names="library,nnamdi azikiwe library,nal,blue building,blue big building,main library,central library,university library,cbt thumbprint centre,freedom square,freedom square & faculty quadrangle,faculty quadrangle",
                category="library",
                description="Huge blue building next to Faculty of Pharmacy and opposite VC's Office; Central University Library where students register for library cards (₦500).",
                photo_path="nnamdi_azikiwke_library.jpeg"
            ),
            "student_affairs": Node(
                formal_name="Student Affairs Building",
                informal_names="student affairs,building for hostel issues,hostel rectification for student building,dark green building,building beside the hostels,student affairs office,student affairs department",
                category="building",
                description="Dark green building beside the hostels row and opposite Carver Building. Center for student welfare and hostel room rectification.",
                photo_path="student_affairs.jpeg"
            ),
            "abj_bldg": Node(
                formal_name="Abuja Building (Prof. Ezeilo Building)",
                informal_names="abuja building,abj building,abj,statistics department,mathematics department,old computer science department,prof ezeilo building,abuja block,abuja lab,abuja labs",
                category="building",
                description="Big brown building housing Statistics, Mathematics, and old Computer Science departments, located near NCSB and Chitis restaurant.",
                photo_path="abuja_building.jpeg"
            ),
            "slt_dept": Node(
                formal_name="Science Laboratory Technology (SLT) Department",
                informal_names="slt,slt department,science lab tech,science lab tech department,science laboratory technology,slt workshop,slt lab,glt lab",
                category="building",
                description="Long brown bungalow building behind FPSLT and near Chitis restaurant; home to Science Laboratory Technology workshops.",
                photo_path="slt_department.jpeg"
            ),
            "ncsb": Node(
                formal_name="New Computer Science Building (NCSB)",
                informal_names="computer science,cs,ncsb,new computer science building,computer science new building,department of computer science,computer science department,new cs,new cs building,ncsb hall",
                category="building",
                description="Modern building with banner 'Welcome to the department of Computer Science', adjacent to Abuja Building.",
                photo_path="computer_science.jpeg"
            ),
            "bello": Node(
                formal_name="Bello Hall (Hostel)",
                informal_names="bello,bello hall,bello hostel,hostel with bello in front,female hostel bello,bello hall unn",
                category="hostel",
                description="Prominent female hostel along the central hostel strip, opposite the Faculty of Pharmacy and Carver Building.",
                photo_path="bello_hostel.jpeg"
            ),
            "vc_office": Node(
                formal_name="Vice-Chancellor's Office (VC's Office)",
                informal_names="vc,vc building,vc office,vcs office,vc's building,vc's office,vc's office opposite library,white building opposite library,university administration",
                category="building",
                description="Big white building opposite Nnamdi Azikiwe Library housing the Vice-Chancellor's office and Central University Administration.",
                photo_path="vc_building_front.jpeg"
            ),
            "odim_gate": Node(
                formal_name="Odim Gate",
                informal_names="odim,odim gate,odim campus gate,hilltop gate",
                category="gate",
                description="University gate leading towards Odim, hilltop hostels, and residential quarters.",
                photo_path="odim_gate.jpeg"
            ),
            "fpslt": Node(
                formal_name="Faculty of Physical Sciences Lecture Theatre (FPSLT)",
                informal_names="fpslt,physical sciences lecture theatre,faculty lecture theatre,science lecture theatre,science theatre,large lecture hall,theatre a",
                category="theatre",
                description="Big red building with a small hut in front, located between Abuja Building and SLT; primary lecture theatre for 100L science classes.",
                photo_path="fpslt.jpeg"
            ),
            "geo": Node(
                formal_name="Geology Department Building",
                informal_names="geology,geology department,geology behind abuja building,earth sciences,geo department,geology block,geo room,glg 111 room",
                category="building",
                description="Two large buildings facing each other through a path between two white barred fences behind Abuja Building.",
                photo_path="geology_department.jpeg"
            ),
            "bookshop": Node(
                formal_name="University Bookshop",
                informal_names="place where they buy book,book shop,book store,school book shop,school book store,place where books are sold,bookshop,university bookshop,sub",
                category="building",
                description="Campus bookstore building with bold 'Book Shop' signboard, located near GS Building and NAL Library.",
                photo_path="bookshop.jpeg"
            ),
            "med_centre": Node(
                formal_name="University Medical Centre",
                informal_names="medical centre,medical center,school hospital,school's hospital,med centre,where doctor is,place where a sick person goes,sick bay,university clinic,medicals",
                category="building",
                description="University health centre compound situated up the hill near Ekpo Refectory Hall.",
                photo_path="medical_center.jpeg"
            ),
            "gs_bldg": Node(
                formal_name="General Studies Building (GS Building)",
                informal_names="gs,gs building,general studies building,place where they do gs class,gs block,gsp building,gsp hall,use of english hall",
                category="building",
                description="Big green building with a large car park in front; primary administrative centre and lecture venue for General Studies courses.",
                photo_path="gs_building.jpeg"
            ),
            "gate_1": Node(
                formal_name="UNN 1st Gate (Main Gate)",
                informal_names="unn 1st gate,1st gate,first gate,unn first gate,entrance gate,main gate,gate at the front of the school,the new gate,unn gate,school gate,town gate,unn main gate",
                category="gate",
                description="Primary front entrance gate of the University of Nigeria, Nsukka along University Road.",
                photo_path="main_gate.jpeg"
            ),
            "gate_2": Node(
                formal_name="UNN 2nd Gate (Abuja / Franco Gate)",
                informal_names="unn 2nd gate,2nd gate,second gate,unn second gate,going out gate,back gate,abuja gate,franco gate,behind flat gate,unn back gate,unn abuja gate,unn franco gate",
                category="gate",
                description="Second gate of the university at the rear side leading out towards Franco and Hilltop.",
                photo_path="abuja_gate.jpeg"
            ),
            "odenigwe_gate": Node(
                formal_name="Odenigwe Campus Gate",
                informal_names="gate that leads to market,odenigwe,odenigwe gate,odenigwe entrance,greenhouse gate",
                category="gate",
                description="Campus entrance gate directly connecting UNN to the Odenigwe community and market.",
                photo_path="odenigwe_gate.jpeg"
            ),
            "aja_nwachukwu": Node(
                formal_name="Aja-Nwachukwu Hall (Hostel)",
                informal_names="hostel,aja,aja-nwachukwu,aja nwachukwu,hostel opposite carver,aja-nwachukwu hall,aja hostel",
                category="hostel",
                description="Student hall of residence joined to Akintola Hall and located directly opposite Carver Building.",
                photo_path="aja_nwachukwu_hostel.jpeg"
            ),
            "akintola": Node(
                formal_name="Akintola Hall (Hostel)",
                informal_names="akintola,akintola hostel,akintola hall",
                category="hostel",
                description="Student hall of residence joined to Aja-Nwachukwu Hall along the hostel row.",
                photo_path="akintola_hostel.jpeg"
            ),
            "eyo_ita": Node(
                formal_name="Eyo-Ita Hall (Hostel)",
                informal_names="eyo-ita,eyo ita,eyo-ita hostel,eyo-ita hall",
                category="hostel",
                description="Student hostel joined to Bello Hall along the main hostel strip.",
                photo_path="eyo_ita_hostel.jpeg"
            ),
            "admission": Node(
                formal_name="Admission Office (Admission Block)",
                informal_names="place where activities for admission are done,admission,admission office,where people collect certificate,admission block,admission building",
                category="building",
                description="Tall cream building near First Bank and printing containers; handles freshman admissions and certificate collection.",
                photo_path="admission_block.jpeg"
            ),
            "ict": Node(
                formal_name="University ICT Centre",
                informal_names="tall white building,ict centre,ict,ict center,computer centre,clionet office,id card centre,school email desk",
                category="building",
                description="Tall white building housing the university information and communication technology facilities.",
                photo_path="ict.jpeg"
            ),
            "lib": Node(
                formal_name="Faculty of Physical Sciences Library",
                informal_names="faculty library,science library,physical science library,faculty lib,science lib,fps library",
                category="library",
                description="Dedicated science faculty library with quiet study desks, reference collections, and faculty past questions.",
                photo_path="faculty_library.jpeg"
            ),
            "canteen": Node(
                formal_name="Faculty Science Canteen & Franco Refectory",
                informal_names="science canteen,faculty canteen,canteen,franco refectory,franco food,snack shop",
                category="cafeteria",
                description="Popular campus dining centre behind the faculty area serving freshly cooked meals and drinks.",
                photo_path="canteen.jpeg"
            ),
            "math": Node(
                formal_name="Mathematics and Statistics Building",
                informal_names="maths block,math department,stats block,statistics department,mathematics department first year classroom,maths room,math 131 room",
                category="building",
                description="Two-storey block housing Mathematics and Statistics classrooms and faculty tutorial halls.",
                photo_path="mathematics.jpeg"
            ),
            "phy": Node(
                formal_name="Physics and Astronomy Building",
                informal_names="physics block,physics department,astronomy block,physics building,observatory dome",
                category="building",
                description="White building with the iconic rooftop astronomical observatory dome.",
                photo_path="physics.jpeg"
            ),
            "chem": Node(
                formal_name="Chemistry Department Building",
                informal_names="chemistry block,chem lab,chemistry department,chemistry,chem,chm",
                category="building",
                description="Building located beside the Geology department housing chemical lecture halls and research laboratories.",
                photo_path="chemistry.jpeg"
            )
        }

        for n in nodes.values():
            db.session.add(n)
        db.session.commit()
        print(f"Added {len(nodes)} campus landmarks and lecture nodes.")

        # 2. CONNECTED WALKWAY EDGES (GRAPH TOPOLOGY WITH GROUND TRUTH DATA)
        raw_routes = [
            # Carver ->
            ("carver", "na_lib", 240, 
             "Looking to your right, standing at the front of the faculty building (Carver), you'll see the Faculty of Pharmacy (cream or brown colored building opposite the hostels row, particularly Bello Hall). Walk through the front of the Faculty of Pharmacy, you'll see a huge blue building next to it. That is the school's library (Nnamdi Azikiwe Library)."),
            ("carver", "student_affairs", 90,
             "Look forward, you'll see a dark green building beside the hostels on the left. Cross the road and walk inside the door with bars. That is the Student Affairs building."),
            ("carver", "abj_bldg", 360,
             "Follow the road immediately at your right beside Carver building (the one you're standing at), you'll meet a junction along with a building, a restaurant labelled 'Chitis'. There's a road still in front that goes into a bushy path, follow that road and keep going towards your right, you'll see a big brown building ahead. That is Abuja building (Prof Ezeilo building)."),
            ("carver", "slt_dept", 250,
             "Follow the road immediately at your right beside Carver building (the one you're standing at), you'll meet a junction along the road with a restaurant, a brown or cream building labelled 'Chitis' in front. Walk in front of it, crossing towards your left, you'll see a path beside Chitis, walk through that path until you see a long building on your left. That is the department of SLT (Science Lab Tech)."),
            ("carver", "ncsb", 380,
             "Follow the road immediately at your right beside Carver building (the one you're standing at), you'll meet a junction up ahead with a cream or brown building, a restaurant labelled 'Chitis'. There's a road still in front of you up ahead that goes into a bushy path, follow that road and keep going towards your right, you'll see a big brown building (Abuja building), walk past it and look next to it, you'll see a new building with a banner labelled 'Welcome to the department of Computer Science'. That is the New Computer Science Building."),
            ("carver", "admission", 610,
             "From the faculty building (Carver) turn right and walk ahead until you meet a junction. At the junction, turn left and walk up ahead. Keep going straight with your eyes on the left until you see a tall cream building near the container where printing is done. That is the Admission building. Walk past the side to see the front of the building."),

            # Bello hostel ->
            ("bello", "carver", 300,
             "Walk towards your right, moving forward until you see a green and white building looking at your left. Cross the road and walk towards the building. That is Carver building (Faculty building for Physical Sciences)."),
            ("bello", "na_lib", 360,
             "Walk towards your left, cross the two way street to the opposite direction and walk up ahead until you see a big blue building. Follow through the gate in front. That is the school's library (Nnamdi Azikiwe Library)."),
            ("bello", "vc_office", 340,
             "Walk towards your left and move towards the roundabout junction. Cross the road and move forward towards a big white building that's opposite a big blue building. Walk around it towards the front. That is the front of the VC's office."),
            ("bello", "student_affairs", 180,
             "Walk towards your right and keep moving forward until you see a dark green building labelled 'Student Affairs'. That is the Student Affairs building."),

            # Odim Gate ->
            ("odim_gate", "abj_bldg", 1260,
             "Keep walking forward from the gate until you meet a T-junction, enter your left and keep moving forward. Stop at a white sign board labelled 'Department of Computer Science' and enter your right. Move ahead until you see a big brown building (Abuja building)."),
            ("odim_gate", "ncsb", 1230,
             "Keep walking forward from the gate until you meet a T-junction, enter your left and keep moving forward. Stop at the white sign board labelled 'Department of Computer Science' and enter your right. Move ahead until you see a new building with a banner labelled 'Welcome to the department of Computer Science' on your left (NCSB)."),
            ("odim_gate", "ict", 1160,
             "Keep walking forward from the gate, walking at the right side of the road until you meet a T-junction, enter your right and move ahead until you see another junction. Enter the left and move ahead until you see a tall white building. That is the school's ICT."),

            # Abuja building ->
            ("abj_bldg", "ncsb", 70,
             "From the front of Abuja building, move towards the right, you'll see a new building with a banner labelled 'Welcome to the department of Computer Science' (NCSB)."),
            ("abj_bldg", "ict", 1080,
             "Walk ahead towards the big trees and follow until you see a small path between two engineering buildings. Follow through, moving ahead and cross the gutter. Cross further unto the other side of the road and move straight, looking at your left. You'll meet a junction, follow your left and move ahead until you see a tall white building. That's the school's ICT."),
            ("abj_bldg", "fpslt", 280,
             "Walk ahead moving forward and looking towards your left. You'll see a mechanic shop, having cars parked in front. Follow towards your left, you'll see a big building with a smaller hut beside or in front of it. Walk past the building and move ahead until you see another big red building with a hut beside or in front as well. That is FPSLT."),
            ("abj_bldg", "geo", 220,
             "Standing in front of Abuja building, follow your right through the road leading to the back of the building. There is a path in between two white barred fences up ahead. Walk through the path until you see two big buildings facing each other. These are Geology department buildings."),

            # FPSLT ->
            ("fpslt", "abj_bldg", 280,
             "From the front of the faculty lecture theatre (FPSLT), move towards your right past the next building and still moving past the mechanic shop where cars are parked in front. Look ahead, you'll see a big brown building. Move ahead to Abuja building."),
            ("fpslt", "ncsb", 293,
             "From the front of the faculty lecture theatre (FPSLT), move towards your right past the next building and still moving past the mechanic shop where cars are parked in front. Look ahead, you'll see a big brown building, there's a new building beside it labelled with a banner 'Welcome to the department of Computer Science'. Move towards the NCSB building."),
            ("fpslt", "slt_dept", 110,
             "From the front of the faculty lecture theatre (FPSLT), move to your left, following the path there. Move straight to the Science Laboratory Technology (SLT) department building."),
            ("fpslt", "ict", 1850,
             "From the front of the faculty lecture theatre move towards your right through the path leading to the Faculty of Engineering with buildings facing each other. Move ahead between the buildings facing each other unto the main road with a Faculty of Engineering sign board on your right. Follow your right and move ahead, cross the road into the other side and move ahead until you meet a T-junction. Enter your left and keep going, you'll meet another junction, enter your left again and move ahead. You'll see a tall white building. That's the school's ICT."),

            # SLT ->
            ("slt_dept", "na_lib", 600,
             "From the front of SLT building follow the path in between the bushes that lead towards the main road in front. Enter your right and cross to the other side of the road. Keep moving a bit, you'll see a small path in between two iron barred fences on your left. Enter your left and keep going forward, you'll have the Faculty of Pharmacy on your left and a shuttle stand path in front. Follow the path towards the right and you'll see a roundabout. Stay on that side of the road, moving ahead, you'll see a big blue building. That's the school's library (NAL)."),
            ("slt_dept", "fpslt", 110,
             "From the front of SLT building, follow the walk path on the left beside the building leading to the back of the building. You'll see a red big building to your right with a hut beside or in front of it (FPSLT)."),
            ("slt_dept", "ict", 1900,
             "From the front of SLT building, follow your right and walk past the big building which is the lecture theatre for biological sciences. Walk towards your right until you arrive at the main road. Stay at your right and keep moving ahead. You'll meet a T-junction, cross to the other side of the road and enter the left. Move ahead until you see another junction, enter your left again and move ahead. You'll see a tall white building. That is the school's ICT."),
            ("slt_dept", "carver", 250,
             "From the front of SLT building, follow your left along the path in between the grasses until you reach a cream or brown building which is a restaurant labelled 'Chitis'. Cross the road to the other side and move to the right at the junction. Move ahead, looking at your left. You'll see a white and green building. That's Carver building (Physical Sciences Faculty Building)."),
            ("slt_dept", "admission", 350,
             "Moving from the front of SLT department building go up ahead, moving through the foot path in between the bushes that lead to the main road. Follow the path that goes towards the right. When you arrive at the main road, cross to the other side of the road and move ahead. Keep going straight looking towards your left until you see a tall cream building beside the container where printing is done. That is the Admission building."),

            # Library (NAL) ->
            ("na_lib", "gs_bldg", 780,
             "Moving from the front of the library, turn to your right and move ahead. Cross the road to the other side and follow the walk path. Move past the car park towards your right and ahead unto the main road. You'll see a big green building with a car park in front. That is the General Studies building."),
            ("na_lib", "carver", 240,
             "Moving from the front of the library, turn to your left and keep going forward. Move past the big cream or brown building (Faculty of Pharmacy) with a car park. Walk past the shuttle bus stop as well. You'll meet a junction and see a tall green and white building. That is the Physical Sciences Faculty Building (Carver)."),
            ("na_lib", "slt_dept", 600,
             "Moving from the front of the library, turn to your left and move ahead, you'll meet the shuttle bus stop and a building with a hut in front where people sit. Follow through the walk path around the hut and walk towards the left. Walk straight up ahead until you reach the main road. Cross the road to the other side, moving towards your right. You'll see a path in between the bushes. Follow that path until you see a long building from your left. That is the department of SLT."),
            ("na_lib", "ict", 1028,
             "Moving from the front of the library, turn to your right and turn right again immediately at the junction to the road beside the library. Move ahead tilting a bit towards the right and walking past First Bank building and also past the container where people print and process documents. Move straight to the road beside the container until you meet the main road. Cross to the other side and move straight forward at the junction in front. Move straight past the building with the 'open quadrangle' (Faculty of Biological Sciences) and go straight ahead. You'll see a tall white building (ICT)."),
            ("na_lib", "admission", 247,
             "Moving from the front of the library, turn to your right and turn right again immediately at the junction to the road beside the library. Move ahead tilting a bit towards the right and walking past First Bank building as well as the container where people print and process documents. Move straight ahead in that direction and look ahead, you'll see a tall cream building. That is the Admission building."),
            ("na_lib", "vc_office", 193,
             "Moving from the front of the library, cross the road to the other side. You'll see a big white building. Walk around it to see the front of the building. That is where the VC's office is."),
            ("na_lib", "bookshop", 255,
             "Moving from the front of the library, turn to your right and cross the road to the other side. Moving along the walk path towards the open car park. Look ahead, you'll see a building with a bold sign that reads Book Shop. That is the school's bookshop."),
            ("na_lib", "student_affairs", 810,
             "Moving from the front of the library, turn to your left and keep going forward. Move past the big cream or brown building with a car park. Walk past the shuttle bus stop as well. You'll meet a junction, cross the two way street unto the other side where the hostels line up. Walk ahead until you see a dark green building labelled 'Student Affairs'. That is the place where students go regarding hostel issues."),

            # Student Affairs ->
            ("student_affairs", "med_centre", 2000,
             "From the front of Student Affairs, turn left and move ahead. Look towards your left, there's a path inside a building that leads to the other end. Follow through that path, you'll see another walk path in between the bushes. Follow that path, heading up the sloping hill until you meet the main road. There is a statue of a woman's face on the left in front of the building (Ekpo ref hall). Keep walking ahead the road up to the junction. Turn left and cross the road to the other side. Walk ahead until you see the Medical Centre white signboard by the right. That is the school's medical centre."),
            ("student_affairs", "carver", 90,
             "From the front of Student Affairs, move forward tilting a bit towards the left. Look at the building opposite you. Cross the two way street, you'll see a green and white building with a car park in front. That is Carver Building (Physical Sciences Faculty Building)."),
            ("student_affairs", "na_lib", 810,
             "From the front of Student Affairs, move forward towards your left. Move ahead towards the junction and cross to the other side, moving towards your right. Look ahead, you'll see a tall blue building. That is the school's Library (NAL)."),
            ("student_affairs", "bookshop", 1085,
             "From the front of Student Affairs, move forward towards your left. Move ahead towards the junction and cross the road to the other side. Move past the white building (VC's building) and go further. At the T-junction by your right turn left into the walk path and follow through it. Look ahead, you'll see a building with a signboard labelled Bookshop. That's the school's bookshop."),

            # Bookshop ->
            ("bookshop", "gs_bldg", 290,
             "From the front of bookshop, turn right and follow the walk path directly beside the bookshop. Move ahead until you meet the main road. Cross the road to the other side. Look ahead, you'll see a big green building with a car park in front. That is the General Studies Building."),
            ("bookshop", "na_lib", 255,
             "From the front of the bookshop, move to your left and follow the walk path until you reach the main road and T-junction. Cross the road to the other side and look ahead, you'll see a big blue building. That is the school's library."),
            ("bookshop", "vc_office", 215,
             "From the front of the book shop, move straight ahead tilting a bit towards your right. Look ahead, you'll see a big white building. That is the VC's office."),

            # NCSB ->
            ("ncsb", "geo", 225,
             "From the front of the new Computer Science building, move to your left and follow the road straight ahead. Keep going straight through the road between the two white barred fences. Look ahead, you'll see two buildings facing each other. That is Geology department."),
            ("ncsb", "abj_bldg", 70,
             "From the front of the new Computer Science building, move to your right and cross the road to the other side. Look ahead, you'll see a tall brown building. That is Abuja building."),

            # Geology ->
            ("geo", "ncsb", 225,
             "From the front of Geology building, move to your left and follow straight ahead through the road between the two white barred fences. Look ahead you'll see a tall brown building on your left (Abuja building) then a new building with a banner written 'Welcome to the department of Computer Science' on your right. That is the new Computer Science building (NCSB)."),
            ("geo", "abj_bldg", 220,
             "From the front of Geology building, move to your left and follow straight ahead through the road between the two white barred fences. Look ahead you'll see a tall brown building on your left. That is Abuja building."),

            # ICT ->
            ("ict", "ncsb", 1120,
             "Moving from the front of ICT, move right to the junction then turn right again and walk until you meet the T-junction. Turn to your right again and cross the road to the other side, cross the gutter unto the walk path and move until you see a building labelled 'Fire Service' looking leftwards. Look further and you'll see a path inside a building that leads to the other end, follow that path and walk straight ahead. Look towards your left, you'll see two buildings beside each other: a tall brown building (Abuja building) and a new building with a banner written 'Welcome to the department of Computer Science' (NCSB)."),
            ("ict", "abj_bldg", 1080,
             "Moving from the front of ICT, move right to the junction then turn right again and walk until you meet the T-junction. Turn to your right again and cross the road to the other side, cross the gutter unto the walk path and move until you see a building labelled 'Fire Service' looking leftwards. Look further and you'll see a path inside a building that leads to the other end, follow that path and walk straight ahead. Look towards your left, you'll see a tall brown building. That is Abuja building."),
            ("ict", "slt_dept", 600,
             "Moving from the front of ICT, move to your right to the junction then turn right again and walk until you meet the T-junction. Cross to the other side of the road and turn right going straight up ahead. When you're almost at the next junction cross the gutter and move to your left, you'll see a big round building which is the biological science lecture theatre. Follow the walk path beside or around it and go straight ahead. Looking ahead you should see a long brown bungalow. That is the department of Science Lab Tech (SLT)."),
            ("ict", "admission", 903,
             "From the front of ICT turn left and walk ahead until you get to the junction. Cross the road to the other side. Look ahead, you'll see a tall cream building. That is the Admission building."),

            # VC Office ->
            ("vc_office", "na_lib", 193,
             "Moving from the front of VC's building, turn right and follow the path beside the building moving forward until you see a tall blue building at the opposite side of the road. Cross the road to the other side. That is the school's library (NAL)."),
            ("vc_office", "bookshop", 215,
             "Moving from the front of VC's building turn right and go straight ahead. Looking ahead, you'll see a building with a signboard written 'Book shop'. That is the school's bookshop."),
            ("vc_office", "student_affairs", 973,
             "Moving from the front of VC's building turn left and walk straight ahead on the path that leads to the main road. Cross the road to the hostels side. Keep going straight past the hostels, moving ahead until you see a dark green building labelled 'Student Affairs' on the right. That is the Student Affairs building."),

            # Admission ->
            ("admission", "na_lib", 247,
             "From the Admission building, turn right and go straight ahead walking past the container where printing is done as well as First Bank building. Turn left at the main road and go straight up the sloping hill. At the junction, turn left. You'll see a tall blue building. That is the school's library (NAL)."),
            ("admission", "carver", 610,
             "From the Admission building, turn right and follow the path immediately beside the building until you reach the main road. At the main road, turn right again and move straight ahead. You'll meet a junction, at the junction turn right and then cross to the other side of the road. Walk ahead until you see a tall green and white building. That is Carver Building (Physical Sciences Faculty building)."),
            ("admission", "ict", 903,
             "From the Admission building, turn right and follow the path immediately beside the building until you reach the main road. At the junction, cross the road to the other side and keep going straight up ahead. Look ahead, you'll see a tall white building. That is the school's ICT."),
            ("admission", "slt_dept", 350,
             "From the Admission building turn left and follow the path immediately beside the building until you reach the main road. At the main road turn right and move ahead. Cross to the other side of the road and move until you see a foot path in between bushes. Follow the foot path, looking ahead. You'll see a long brown bungalow. That is the department of Science Lab Tech (SLT)."),

            # GS Building ->
            ("gs_bldg", "bookshop", 290,
             "From the front of GS building, following the side road of the building cross to the other side of the road, you'll see a building that has a car park facing the side of GS building. Walk ahead beside that building, following through the foot path beside the building (the right side). This will lead you to the back. Look left towards the back of the building, you'll see a building with a signboard that says 'Book Shop'. That is the school's bookshop."),
            ("gs_bldg", "na_lib", 780,
             "From the front of GS building move to the main road beside GS building and cross to the other side where there's a building with an open car park facing GS building. Follow through the car park and move straight ahead. Looking forward, you'll see a tall blue building. Move to it and cross the road to reach NAL Library."),

            # Medical Centre ->
            ("med_centre", "student_affairs", 2000,
             "From the front of Medical Centre cross the road to the other side and move towards your left. Keep moving until you see a T-junction. Follow the right leading downwards the hill. Keep going straight, passing the building having a statue of a woman's face beside it (Ekpo ref hall). Keep going straight and walk through the foot path in between the buildings. You'll see hostels on your left and you'll see a T-junction. Turn right just before the T-junction and move straight until you see a green building labelled 'Student Affairs'. That is the Student Affairs Building."),

            # 1st Gate (Main Gate) ->
            ("gate_1", "med_centre", 3100,
             "Entering through the first gate (Main Gate), go straight. When you reach the junction, turn left and go straight. You'll meet another junction. When you reach the next junction, turn right and go straight keeping your eye on the right. You'll see a building compound with a sign board in front up a hill by the right of the road. That is the school's medical centre."),
            ("gate_1", "gs_bldg", 2886,
             "Entering through the first gate (Main Gate), go straight. When you reach the junction, turn left and go straight. You'll meet another junction, keep straight, you'll see another junction again. Turn right and go straight. Look at the left side of the road, you'll see a green building with a car park in front of it. That is the General Studies building."),

            # 2nd Gate (Abuja/Franco Gate) ->
            ("gate_2", "ict", 905,
             "Entering through the back gate (2nd Gate / Franco Gate), move straight. You'll meet a junction, keep going straight. At the next junction, turn right and look ahead, you'll see a tall white building. That is the school's ICT."),

            # Odenigwe Gate ->
            ("odenigwe_gate", "med_centre", 3000,
             "Coming from Odenigwe gate, go straight. You'll meet a junction, keep going straight. At the next junction, keep on going straight. Then you'll meet a T-junction with a primary school at the other side of the road, turn right and go straight. Keep going straight, keeping your eye on the right side of the road. You'll see a compound up a hill with buildings inside along with cars parked as well as a sign board in front. That is the school's medical centre."),
            ("odenigwe_gate", "vc_office", 2867,
             "Coming from Odenigwe gate, go straight. You'll meet a junction, keep going straight. At the next junction, keep going straight. Then you'll meet a T-junction with a primary school at the other side of the road, turn right and go straight. Move past the school, with your eye on the left side of the road. You'll see a major road leading to the left with a sign board that says Education where shuttle buses stop. Turn left and go straight passing through the building that leads to the other end. Keep going straight, look ahead, you'll see a big white building. That is the VC's building."),
            ("odenigwe_gate", "gs_bldg", 2309,
             "Coming from Odenigwe gate, go straight. You'll meet a junction, keep going straight. At the next junction, keep going straight. Then you'll meet a T-junction with a primary school at the other side of the road, turn left and go straight. Keep your eyes on the right side of the road, you'll see a foot path between two iron fences. Go through that path and keep going straight. You'll come out at a main road. Move towards your right and cross the road. Look ahead, you'll see a green building with a car park in front of it. That is the General Studies building."),

            # Hostels: Aja-Nwachukwu, Akintola, Eyo-Ita ->
            ("aja_nwachukwu", "na_lib", 405,
             "Coming from the hostel (Aja-Nwachukwu Hall), move forward to the main road and turn left. Do not cross the road yet. Keep going forward until you reach the roundabout junction and then cross towards your right. Look ahead, you'll see a tall blue building. That is the school's library (NAL)."),
            ("aja_nwachukwu", "student_affairs", 125,
             "Coming from the hostel (Aja-Nwachukwu Hall), move towards your left through the foot path. Look left, you'll see a green building labelled 'Student Affairs'. That is the Student Affairs building."),
            ("aja_nwachukwu", "carver", 182,
             "Coming from the hostel (Aja-Nwachukwu Hall), move towards your left through the foot path. Cross the gutter unto one side of the road then cross the two way street and look ahead. You'll see a white and green building with a car park in front of it. That is Carver Building (Physical Sciences Faculty Building)."),
            ("akintola", "aja_nwachukwu", 75,
             "Coming from the hostel (Akintola Hall), move forward towards your left through the foot path, you'll see another hostel joined to the hostel named Aja-Nwachukwu. That is Aja-Nwachukwu Hall."),
            ("eyo_ita", "bello", 78,
             "Coming from the hostel (Eyo-Ita Hall), move forward towards your right through the foot path, you'll see another hostel joined to the hostel named Bello Hall. That is Bello Hall."),
            ("eyo_ita", "na_lib", 347,
             "Coming from the hostel (Eyo-Ita Hall), move forward towards your left through the foot path, you'll meet a main road. Cross to the other side of the road and look ahead towards your right, you'll see a tall blue building. Move towards it. That is the school's Library (NAL)."),
            ("eyo_ita", "vc_office", 327,
             "Coming from the hostel (Eyo-Ita Hall), move forward towards your left through the foot path, you'll meet a main road. Cross to the other side of the road and keep moving forward inside the circular seat out. Move through the path and look ahead, you'll see a big white building. That is the VC's building. Take from your left to get to the front of the building.")
        ]

        # Faculty Intra-Network links (Math, Physics, Chemistry, Faculty Library, Canteen)
        faculty_links = [
            ("math", "abj_bldg", 60, "Exit the Mathematics block and cross the connecting corridor into Abuja Building."),
            ("abj_bldg", "math", 60, "From Abuja Building, walk through the ground-floor connecting corridor into Mathematics and Statistics."),
            ("phy", "carver", 80, "Exit the Physics and Astronomy block and take the paved walkway directly into Carver Building."),
            ("carver", "phy", 80, "Exit Carver Building and head along the covered path leading directly to the Physics and Astronomy Building."),
            ("chem", "geo", 70, "Walk along the shared walkway connecting Chemistry to the adjacent Geology Department Building."),
            ("geo", "chem", 70, "Walk past the Geology rock display along the path leading directly into the Chemistry Department Building."),
            ("lib", "carver", 50, "Walk along the faculty veranda connecting Carver Building directly to the Faculty of Physical Sciences Library."),
            ("carver", "lib", 50, "Exit Carver Building and take the right corridor leading into the Faculty of Physical Sciences Library."),
            ("canteen", "slt_dept", 60, "Exit the Science Canteen and take the direct pathway leading to the Science Laboratory Technology (SLT) building."),
            ("slt_dept", "canteen", 60, "From the SLT department, follow the short paved path leading to the Faculty Science Canteen.")
        ]

        # Index known routes for reverse lookups
        known_routes = {}
        for u_key, v_key, secs, instr in raw_routes:
            known_routes[(u_key, v_key)] = (secs, instr)
        for u_key, v_key, secs, instr in faculty_links:
            known_routes[(u_key, v_key)] = (secs, instr)

        # Build complete bidirectional graph edges
        all_edges = []
        added_pairs = set()

        for (u_key, v_key), (secs, instr) in list(known_routes.items()):
            u_node = nodes[u_key]
            v_node = nodes[v_key]
            dist = round(secs * 1.25)
            all_edges.append(Edge(
                source_node_id=u_node.node_id,
                destination_node_id=v_node.node_id,
                instruction=instr,
                distance_meters=dist,
                foot_accessible=True
            ))

            # Ensure reverse edge exists
            rev_key = (v_key, u_key)
            if rev_key not in known_routes and rev_key not in added_pairs:
                rev_instr = f"From {v_node.formal_name}, follow the pedestrian walkway retracing the path towards {u_node.formal_name}."
                all_edges.append(Edge(
                    source_node_id=v_node.node_id,
                    destination_node_id=u_node.node_id,
                    instruction=rev_instr,
                    distance_meters=dist,
                    foot_accessible=True
                ))
                added_pairs.add(rev_key)

        for edge in all_edges:
            db.session.add(edge)
        db.session.commit()
        print(f"Added {len(all_edges)} walkway edges with ground-truth distance & timings.")

        # 3. VERIFIED FRESHMAN ONBOARDING KNOWLEDGE BASE (FAQS)
        kb_entries = [
            OrientationKB(
                category="clearance",
                question_pattern="clearance,faculty clearance,how to do clearance,clearance documents,carver clearance,clearance steps,requirements for clearance,faculty officer,freshman clearance,freshers clearance,clerance",
                answer="""📋 **Official Faculty Clearance Requirements (Faculty of Physical Sciences):**


• **Venue**: **Carver Building**, Faculty General Office (Ground Floor).

• **Action**: Submit your credentials in a standard green file jacket to the Faculty Officer.


**Required Documents to Arrange Inside Your File Jacket**:

1. Official UNN Provisional Admission Letter (printed from portal).

2. Original JAMB Admission Letter.

3. Original JAMB Result Slip.

4. Acceptance Fee Official Receipt (Remita RRR printout).

5. O'Level Result(s) — WAEC, NECO, or NABTEB scratch cards or verified printouts.

6. Birth Certificate or National Population Commission (NPC) Declaration of Age.

7. Letter of Attestation of Good Character (from a Clergy, Traditional Ruler, or Senior Civil Servant).

8. Local Government Area (LGA) Letter of Identification / Origin.

9. Recent Passport Photographs (at least 6-8 red or white background copies).
""".strip()
            ),
            OrientationKB(
                category="clearance_deadline",
                question_pattern="clearance deadline,last day for clearance,when is clearance closing,deadline for clearance,clearance date",
                answer="""⏳ **Faculty Clearance Deadline:**


Faculty clearance for all 100-Level freshmen typically closes **4 to 6 weeks** following official portal opening and resumption.

⚠️ *Failure to complete physical clearance at Carver Building before matriculation forfeits your provisional admission status.*
""".strip()
            ),
            OrientationKB(
                category="fees",
                question_pattern="school fees,how to pay fees,pay fees,fees breakdown,acceptance fee,rrr,remita,invoice,bank payment,school charges,how much is school fees",
                answer="""💳 **School Fees Payment Procedure:**


1. Log into the official UNN portal (`unnportal.unn.edu.ng`) using your JAMB Registration Number.

2. Navigate to **School Fees** $\rightarrow$ **Generate Invoice**.

3. Your unique 12-digit **Remita Retrieval Reference (RRR)** will generate.

4. Pay securely online via ATM Card / Internet Banking or print the invoice and pay at any commercial bank branch.

5. Return to the portal, verify payment with your RRR, and print the official university receipt.
""".strip()
            ),
            OrientationKB(
                category="registration_steps",
                question_pattern="course registration,how to register courses,portal registration,register courses,academic adviser,sign course form,print course form,course reg",
                answer="""📝 **First-Semester Course Registration Procedure:**


1. **Clearance First**: Ensure you have completed Faculty Clearance at Carver Building.

2. **Online Registration**: Log into `unnportal.unn.edu.ng` $\rightarrow$ 'Course Registration'.

3. Select all compulsory faculty core courses (e.g. MTH 111, MTH 121, PHY 115, CHM 101, COS 101, GSP 101, GSP 111).

4. Submit and print four (4) hard copies of your Course Registration Slip.

5. **Signatures Required**: Take your printed slips to your Departmental Academic Adviser, Head of Department (HOD), and Faculty Dean at Carver Building for endorsements.
""".strip()
            ),
            OrientationKB(
                category="library",
                question_pattern="library registration,library card,how to register for library card,nal library,use library,register library,library passport,nal registration,library fee,500 library",
                answer="""📚 **Nnamdi Azikiwe Library (NAL) Registration:**


• **Venue**: Nnamdi Azikiwe Library (NAL - Main Library), Circulation Desk.

• **Requirements to Bring**:

  1. One (1) recent passport photograph.

  2. Printed official UNN School Fees Receipt.

  3. Fee of **₦500** cash.

• **Procedure**: Fill out the library user bio-data card with your details. You will be scheduled to return on a designated date to collect your laminated physical Library Card.
""".strip()
            ),
            OrientationKB(
                category="library",
                question_pattern="cbt thumbprint,cbt verification,thumbprint for cbt,cbt exams,cbt registration,biometric thumbprinting",
                answer="""💻 **CBT Biometric Thumbprinting:**


• **Why Required**: Mandatory for all 100-Level students to write computer-based General Studies (GS) and university exams.

• **Where Done**: Designated CBT verification desk at the Nnamdi Azikiwe Library or University ICT Centre.

• **Action**: Present your student profile slip and school fees receipt, and capture your digital fingerprints.
""".strip()
            ),
            OrientationKB(
                category="id_card",
                question_pattern="student id card,id card,get id card,id card capture,collect id card,ict id card,identity card,plastic id card",
                answer="""🪪 **Student ID Card Processing & Collection:**


• **Location**: **University ICT Centre**.

• **Requirements to Bring**:

  1. Printed official School Fees Receipt.

  2. Printed UNN Admission Letter / Profile Slip.

• **Biometric Capture**: The ICT staff will capture your digital passport photograph and electronic fingerprints, and verify your personal details.

• **Collection**: ID cards are produced in departmental batches. Present your faculty dues receipt and student identification slip to collect your physical plastic ID card on the announced collection date.
""".strip()
            ),
            OrientationKB(
                category="academics",
                question_pattern="general studies,gs courses,gsp,gs building,gs registration,gs handbook,gsp 101,gsp 111,bookshop gs,class rep gs",
                answer="""📖 **General Studies (GS / GSP) Registration:**


1. **Payment & Handbook**: Pay the designated fee to your departmental Class Representative or purchase your official GS course handbook directly from the **University Bookshop** (ensure you get an official receipt).

2. **GS Building Registration**: Take your receipt and course form to the **General Studies Building (GS Building)** to complete registration with the GS Directorate.

3. **100L First Semester GS Courses**:

  • **GSP 101 (Use of English I)**: Wednesdays 8:00 AM – 10:00 AM at the General Studies Building.

  • **GSP 111 (Use of Library & Study Skills)**: Wednesdays 10:00 AM – 12:00 PM at FPSLT.
""".strip()
            ),
            OrientationKB(
                category="wifi",
                question_pattern="school email,unn email,clionet,wifi,campus wifi,clionet password,student email,internet,ict email",
                answer="""🌐 **UNN School Email & Campus Wi-Fi (Clionet) Access:**


• **Location**: **University ICT Centre**.

• **How to Get School Email**:

  - Present your printed School Fees Receipt at the customer service desk.

  - Your official university email (`firstname.lastname.regno@unn.edu.ng`) will be generated on the spot.

• **How to Connect to Clionet Wi-Fi**:

  - Present your newly generated school email and fees receipt to the network administrator at the ICT Centre.

  - You will be issued your personal Clionet Wi-Fi login password to access high-speed internet across campus hotspot zones.
""".strip()
            ),
            OrientationKB(
                category="medicals",
                question_pattern="medical centre,medicals,medical registration,open medical file,hospital,clinic,health centre,100,200,medical file",
                answer="""🏥 **University Medical Centre Registration:**


• **Location**: University Medical Centre (Health Centre).

• **Requirements to Bring**:

  1. Cash sum of **₦100 to ₦200** to purchase and open your medical record folder.

  2. Your UNN Registration Number (or JAMB Reg Number).

• **Procedure**: Fill out the medical history form inside your new folder and return it to the records desk for formal filing. Once registered, you have access to free consultations and subsidized emergency medications throughout your studies.
""".strip()
            ),
            OrientationKB(
                category="hostel",
                question_pattern="hostel allocation,booting hostel,bed space,apply hostel,hostel payment,hostel requirements,accommodation,campus accommodation,how do i get a hostel,hostel accommodation,porter,mattress,squatting,makintouch,pillowcases,bedspreads,supervisor fees",
                answer="""🏠 **Hostel Allocation ('Booting') & Check-In Guide:**


**1. Prerequisites & Preparation**:

• Ensure your school fees are fully paid.

• Stay active on departmental WhatsApp groups for sudden announcements on when the portal opens.

• **'Fast Fingers' Required**: Bed spaces exhaust within minutes. Research your preferred hostels beforehand (e.g., Bello, Okpara, Mary Slessor for females; Eni-Njoku, Alvan, Franco for males), but be flexible and pick alternative hostels immediately if your top choice fills up.


**2. Application & Payment**:

• Log into the portal $\\rightarrow$ 'Hostel Allocation' $\\rightarrow$ 'Apply for Bed Space'.

• Generate Remita RRR invoice (strictly valid for 2–3 days only).

• Pay immediately via online card, transfer, or bank branch.

• Return to the portal with your RRR to authenticate payment and print the official Hostel Allocation Slip & Payment Receipt.


**3. Check-In with Hall Porters**:

• Present printed allocation slips at the hostel porter's lodge.

• **Compulsory Items to Bring**: 1 Makintouch mattress, 2 pillowcases, and 2 bedspreads (bedsheets).

• Pay the hostel supervisor maintenance fee to receive your room key.

⚠️ *Important Notice: Squatting or selling bed spaces is strictly prohibited and attracts disciplinary action by the University Senate.*
""".strip()
            ),
            OrientationKB(
                category="cgpa",
                question_pattern="cgpa,gpa,grading scale,how is cgpa calculated,calculate cgpa,5 point scale,grade points,first class cgpa,second class upper,degree classification,grading,grades",
                answer="""🎓 **UNN 5-Point Grading Scale & CGPA Calculation:**

• **Grading Scale**:
  - **A** (70% – 100%): 5 Points (Excellent)
  - **B** (60% – 69%): 4 Points (Very Good)
  - **C** (50% – 59%): 3 Points (Good)
  - **D** (45% – 49%): 2 Points (Pass)
  - **F** (0% – 44%): 0 Points (Fail)

• **How CGPA is Calculated**:
  $$\\text{GPA} = \\frac{\\sum (\\text{Course Credit Units} \\times \\text{Grade Points})}{\\sum \\text{Total Credit Units}}$$
  *Example*: Scoring an **A** (5 pts) in a 3-unit course (e.g. MTH 111) yields $3 \\times 5 = 15$ Quality Points.

• **Degree Classifications (UNN Standard)**:
  - **First Class Honours**: 4.50 – 5.00 CGPA
  - **Second Class Honours (Upper Division / 2:1)**: 3.50 – 4.49 CGPA
  - **Second Class Honours (Lower Division / 2:2)**: 2.40 – 3.49 CGPA
  - **Third Class Honours**: 1.50 – 2.39 CGPA
  - **Pass**: 1.00 – 1.49 CGPA""".strip()
            )
        ]

        for kb in kb_entries:
            db.session.add(kb)
        db.session.commit()
        print(f"Added {len(kb_entries)} verified onboarding & clearance QA guides.")

        # 4. OFFICIAL CAMPUS & FACULTY EVENTS
        events = [
            Event(
                title="Faculty of Physical Sciences 100L Orientation",
                date_time="3-4 Weeks After Resumption (10:00 AM)",
                venue="Faculty of Physical Sciences Lecture Theatre (FPSLT)"
            ),
            Event(
                title="UNN Official Matriculation Ceremony for Freshmen",
                date_time="Date Announced by University Senate (09:00 AM)",
                venue="Freedom Square & Faculty Quadrangle"
            ),
            Event(
                title="100-Level Departmental Freshers Meetings",
                date_time="Scheduled by Respective Departmental Staff",
                venue="Departmental Lecture Venues (NCSB, Carver, Maths, Geology)"
            )
        ]

        for ev in events:
            db.session.add(ev)
        db.session.commit()
        print(f"Added {len(events)} official faculty events.")

        # 5. AUTHENTIC 100L FIRST-SEMESTER LECTURE TIMETABLES (8 TRACKS)
        # Raw timetable schedule mapping
        timetable_raw = [
            # 1. Computer Science
            ("Computer Science", "COS 101", "Introduction to Computing Sciences (3 Units)", "Monday", "10:00 AM - 12:00 PM", "New Computer Science Building (NCSB)"),
            ("Computer Science", "MTH 111", "Elementary Mathematics I (Algebra & Trig - 3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Computer Science", "MTH 121", "Elementary Mathematics II (Calculus - 3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Computer Science", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Computer Science", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Computer Science", "COS 141", "Computing Practice (2 Units)", "Tuesday", "02:00 PM - 04:00 PM", "New Computer Science Building (NCSB)"),
            ("Computer Science", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Computer Science", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 2. Computer Science & Statistics
            ("Computer Science & Statistics", "COS 101", "Introduction to Computing Sciences (3 Units)", "Monday", "10:00 AM - 12:00 PM", "New Computer Science Building (NCSB)"),
            ("Computer Science & Statistics", "MTH 111", "Elementary Mathematics I (3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Computer Science & Statistics", "MTH 121", "Elementary Mathematics II (Calculus - 3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Computer Science & Statistics", "STA 111", "Probability I (2 Units)", "Monday", "08:00 AM - 10:00 AM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Computer Science & Statistics", "STA 131", "Statistical Inference I (2 Units)", "Wednesday", "02:00 PM - 04:00 PM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Computer Science & Statistics", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Computer Science & Statistics", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Computer Science & Statistics", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Computer Science & Statistics", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 3. Statistics
            ("Statistics", "STA 111", "Probability I (2 Units)", "Monday", "08:00 AM - 10:00 AM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Statistics", "STA 131", "Statistical Inference I (2 Units)", "Wednesday", "02:00 PM - 04:00 PM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Statistics", "STA 172", "Statistical Computing I (2 Units)", "Friday", "10:00 AM - 12:00 PM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Statistics", "MTH 111", "Elementary Mathematics I (3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Statistics", "MTH 121", "Elementary Mathematics II (3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Statistics", "COS 101", "Introduction to Computing Sciences (3 Units)", "Monday", "10:00 AM - 12:00 PM", "New Computer Science Building (NCSB)"),
            ("Statistics", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Statistics", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 4. Geology
            ("Geology", "GLG 111", "Physical Geology (2 Units)", "Monday", "08:00 AM - 10:00 AM", "Geology Department Building"),
            ("Geology", "GLG 141", "Earth History (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "Geology Department Building"),
            ("Geology", "GLG 171", "Introduction to Field Mapping (1 Unit)", "Friday", "02:00 PM - 05:00 PM", "Geology Department Building"),
            ("Geology", "CHM 101", "Basic Principles of Chemistry I (2 Units)", "Tuesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Geology", "CHM 171", "Basic Practical Chemistry (1 Unit)", "Tuesday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Geology", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Geology", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Geology", "MTH 111", "Elementary Mathematics I (3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Geology", "MTH 121", "Elementary Mathematics II (3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Geology", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Geology", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 5. Science Laboratory Technology (SLT)
            ("Science Laboratory Technology", "SLT 101", "Introduction to Science Lab Technology (2 Units)", "Monday", "10:00 AM - 12:00 PM", "Science Laboratory Technology (SLT) Department"),
            ("Science Laboratory Technology", "GLT 101", "Laboratory Hazards and Safety (2 Units)", "Tuesday", "10:00 AM - 12:00 PM", "Science Laboratory Technology (SLT) Department"),
            ("Science Laboratory Technology", "CHM 101", "Basic Principles of Chemistry I (2 Units)", "Tuesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Science Laboratory Technology", "CHM 171", "Basic Practical Chemistry (1 Unit)", "Wednesday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Science Laboratory Technology", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Science Laboratory Technology", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Science Laboratory Technology", "BIO 151", "General Biology I (3 Units)", "Thursday", "08:00 AM - 10:00 AM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Science Laboratory Technology", "MTH 111", "Elementary Mathematics I (3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Science Laboratory Technology", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Science Laboratory Technology", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 6. Mathematics
            ("Mathematics", "MTH 111", "Elementary Mathematics I (Algebra & Trig - 3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Mathematics", "MTH 121", "Elementary Mathematics II (Calculus - 3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Mathematics", "MTH 131", "Set Theory and Logic (2 Units)", "Friday", "10:00 AM - 12:00 PM", "Mathematics and Statistics Building"),
            ("Mathematics", "COS 101", "Introduction to Computing Sciences (3 Units)", "Monday", "10:00 AM - 12:00 PM", "New Computer Science Building (NCSB)"),
            ("Mathematics", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Mathematics", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Mathematics", "STA 111", "Probability I (2 Units)", "Monday", "08:00 AM - 10:00 AM", "Abuja Building (Prof. Ezeilo Building)"),
            ("Mathematics", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Mathematics", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 7. Physics & Astronomy
            ("Physics & Astronomy", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Physics & Astronomy", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Physics & Astronomy", "PHY 121", "Fundamentals of Mechanics (2 Units)", "Monday", "10:00 AM - 12:00 PM", "Carver Building"),
            ("Physics & Astronomy", "AST 101", "Introduction to Astronomy (2 Units)", "Wednesday", "02:00 PM - 04:00 PM", "Physics and Astronomy Building"),
            ("Physics & Astronomy", "MTH 111", "Elementary Mathematics I (3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Physics & Astronomy", "MTH 121", "Elementary Mathematics II (3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Physics & Astronomy", "CHM 101", "Basic Principles of Chemistry I (2 Units)", "Tuesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Physics & Astronomy", "COS 101", "Introduction to Computing Sciences (3 Units)", "Monday", "10:00 AM - 12:00 PM", "New Computer Science Building (NCSB)"),
            ("Physics & Astronomy", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Physics & Astronomy", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),

            # 8. Pure & Industrial Chemistry
            ("Pure & Industrial Chemistry", "CHM 101", "Basic Principles of Chemistry I (2 Units)", "Tuesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Pure & Industrial Chemistry", "CHM 111", "General Inorganic Chemistry (2 Units)", "Monday", "08:00 AM - 10:00 AM", "Carver Building"),
            ("Pure & Industrial Chemistry", "CHM 171", "Basic Practical Chemistry (1 Unit)", "Tuesday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Pure & Industrial Chemistry", "ICH 101", "Introduction to Industrial Chemistry (2 Units)", "Thursday", "02:00 PM - 04:00 PM", "Chemistry Department Building"),
            ("Pure & Industrial Chemistry", "PHY 115", "General Physics for Physical Sciences I (2 Units)", "Friday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Pure & Industrial Chemistry", "PHY 191", "Practical Physics I (1 Unit)", "Thursday", "02:00 PM - 05:00 PM", "Abuja Building Laboratories"),
            ("Pure & Industrial Chemistry", "MTH 111", "Elementary Mathematics I (3 Units)", "Tuesday", "08:00 AM - 10:00 AM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Pure & Industrial Chemistry", "MTH 121", "Elementary Mathematics II (3 Units)", "Thursday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("Pure & Industrial Chemistry", "GSP 101", "Use of English I (2 Units)", "Wednesday", "08:00 AM - 10:00 AM", "General Studies Building (GS Building)"),
            ("Pure & Industrial Chemistry", "GSP 111", "Use of Library & Study Skills (2 Units)", "Wednesday", "10:00 AM - 12:00 PM", "Faculty of Physical Sciences Lecture Theatre (FPSLT)")
        ]

        for dept, code, title, day, time_slot, venue in timetable_raw:
            entry = Timetable(
                department=dept,
                course_code=code,
                course_title=title,
                day=day,
                time=time_slot,
                venue=venue
            )
            db.session.add(entry)
        db.session.commit()
        print(f"Added {len(timetable_raw)} official departmental timetable rows.")

        print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
