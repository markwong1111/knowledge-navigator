import asyncio
from pathlib import Path
from typing import List, Dict, Union, Optional
import pandas as pd

from src.file_reader import read_text_file, read_csv_file, read_pdf_file, read_doc_file
from src.associational_algorithm import AssociationalOntologyCreator
from src.generate_knowledge_graph import visualize_graph


async def generate_knowledge_graph_html(
    files: Optional[List[Dict[str, Union[str, bytes]]]] = None,
    raw_text: Optional[str] = None
) -> Optional[str]:
    """
    Generate a knowledge graph HTML from uploaded files or raw text.
    
    Args:
        files: List of file dictionaries with keys:
            - 'name': filename (str)
            - 'content': file content as bytes or file-like object
            - 'extension': file extension (e.g., '.txt', '.pdf', '.csv', '.docx')
        raw_text: Optional raw text string to process
    
    Returns:
        - HTML string of the knowledge graph (or None if error)
    """
    # result = {
    #     'html': None,
    #     'graph_data': None,
    #     'error': None,
    #     'processed_text': None
    # }
    
    # Step 1: Read and process document content
    full_text = []
    
    if raw_text:
        full_text.append({"name": "raw_text", "content": raw_text})
    
    if files:
        for file_dict in files:
            file_name = file_dict.get('name', 'unknown')
            file_content = file_dict.get('content')
            file_extension = file_dict.get('extension', Path(file_name).suffix).lower()
            
            try:
                if file_extension == ".txt":
                    text_content = read_text_file(file_content)
                    full_text.append({"name": file_name, "content": text_content})
                    
                elif file_extension == ".csv":
                    df = read_csv_file(file_content)
                    if df is not None:
                        full_text.append({"name": file_name, "content": df})
                        
                elif file_extension == ".pdf":
                    pdf_content = read_pdf_file(file_content)
                    full_text.append({"name": file_name, "content": pdf_content})
                    
                elif file_extension == ".docx":
                    doc_content = read_doc_file(file_content)
                    full_text.append({"name": file_name, "content": doc_content})
                    
                else:
                    # result['error'] = f"Unsupported file type: {file_name}"
                    # return result
                    return None
                    
            except Exception as e:
                # result['error'] = f"Error reading file {file_name}: {str(e)}"
                # return result
                return None
    
    # Check if we have any content to process
    if not full_text:
        # result['error'] = "No content provided. Please provide files or raw text."
        # return result
        return None
    
    # Step 2: Generate the knowledge graph
    try:
        creator = AssociationalOntologyCreator(llm_name="", api_key="") #this is where we would pass in the AI connection info
        graph_document = await creator.create_associational_ontology(full_text)
        
        # Validate graph document
        if graph_document and graph_document.nodes:
            html_output = visualize_graph(graph_document)
            return html_output
        else:
            # result['error'] = "Graph generation failed: No valid nodes or relationships were extracted from the text."
            return None

            
    except Exception as e:
        # result['error'] = f"An error occurred during graph generation: {str(e)}"
        return None
    
    # return result['html']


def generate_knowledge_graph_html_sync(
    files: Optional[List[Dict[str, Union[str, bytes]]]] = None,
    raw_text: Optional[str] = None
) -> Optional[str]:
    """
    Synchronous wrapper for generate_knowledge_graph_html.
    
    Args:
        files: List of file dictionaries (see async version for details)
        raw_text: Optional raw text string to process
    
    Returns:
        HTML string (or None if error)
    """
    return asyncio.run(generate_knowledge_graph_html(files, raw_text))


# Example usage:
if __name__ == "__main__":
    # Example 1: Process raw text
    raw_text = """
    In The Beginning
In the beginning, there were only the Aether and Keepers. Among them were two beings who would later be known by many names. One would be known as Doctor Monty, the other being as the Shadowman. In time, the Keepers crafted the Summoning Key, a device that allows them to manipulate the Aether. Holding power over reality itself, they used it to create Agartha. The Keepers later mastered the ability to travel between dimensions.

At some point, several Keepers, among which the Shadowman, began experimenting with the Dark Aether, an energy beneath creation. The Dark Aether corrupted and corroded their souls, and the corrupted Keepers became known as the Apothicons.

The Apothicons created the Aether Pyramid, a device capable of absolute power. A schism formed between them and the Keepers untainted by the Dark Aether. Soon after, a war broke out between Apothicons and uncorrupted Keepers. Facing defeat, the Apothicons hid the Aether Pyramid on a moon within one of the newly discovered dimensions. After banishing the Apothicons to the Dark Aether, the remaining Keepers took on the mantle of Guardians. Trapped in the Dark Aether, the Apothicons evolved over eons into twisted creatures that now bear little resemblance to their Keeper brethren. They desired, above all else, to return to Agartha.

By September 5 CE, the Apothicons, knowing the Earth has a gateway to Agartha, sent meteors containing Element 115 to the planet in different dimensions across space and time. They believe humanity will one day use Element 115 to wage war among themselves, opening a rift that will allow the Apothicons to escape the Dark Aether.

The Great War
On January 15th, 1292, the Great War between humanity (including the Wolf King) and the Apothicons began across dimensions. During the war, Sir Pablo Marinus was saved from the clutches of a Margwa by four heroes known as Primis. On December 31st, 1299, after more than seven years of war, Primis (with the Keepers and the rest of humanity) defeated the Apothicons, bringing the Great War to an end. Before they seemingly disappeared from history, Primis instructed the Wolf King to begin building his castle that would later be known as Der Eisendrache.

Several years later, honoring the Wolf King's dying request, his loyal servant Arthur scattered and buried his bones in the grounds of Der Eisendrache, accompanied by the King's Wolf. Arthur was then teleported by temporal rifts to Resolution 1295 in 2025 Angola.

Ultimis Story
In 1885, a blacksmith named Jebediah Brown was living in a mining town called Purgatory Point in the Old West. The mine contained large amounts of Element 115 which started to affect people who went down there. One of the miners turned into a zombie and attacked Jebediah's mother, killing her. Wanting to find answers, Jebediah went down in the mine where he spent five days without realizing it. Later, on April 19th, Jebediah had a vision in his sleep. Two angels asked him to build a machine, a Pack-a-Punch Machine, which became a success in the town. On June 30th, Jebediah had another vision; the two angels asked him to create an Agarthan Device. The Agarthan Device had three components: the blood of an elder god found at the bottom of the ocean, an Elemental Shard created by forging four human souls to a rock of Element 115, and a metallic Vril vessel. Jeb managed to craft the vessel, but had no means of obtaining the blood or the souls.

After crafting the Vril Vessel, Jebediah upgraded it with the Pack-a-Punch. As a result of this, and the fracturing of the Earth after Ultimis helped Maxis launch rockets from the Moon in 2025, a temporal rift was created, transporting the entire town, including Jebediah, to an underground cavern in Angola. Afterwards, zombies began to overrun the now buried town, killing its inhabitants including Jebediah.

On June 30th, 1908, a meteor containing Element 115 crashed near the Stony Tunguska River in Siberia. Over the next decades, more deposits of Element 115 were discovered in Germany, Japan, the United States of America and on the Moon.

In 1931, after a large deposit of Element 115 was found in Breslau, Doctor Ludvig Maxis formed Group 935 as an international German-led research team, becoming its head scientist. The Der Riese facility was established at Breslau. Maxis sought to use the newly discovered element to improve the human condition by developing advanced technologies. He invited Doctor Edward Richtofen, who would later be known as Ultimis Richtofen, to join Group 935. Richtofen agreed, secretly acting on behalf of the Illuminati's interests.

By 1939, Maxis and Ultimis Richtofen started working on the first teleportation experiments with a Matter Transference Prototype. The experiments were unsuccessful. The subjects were teleported, but their chemical composition was altered, leaving them catatonic and changed. Ultimis Richtofen also began the development of the Wunderwaffe DG-2. In the same year, Maxis turned to the Reichstag and the Nazi Party for additional funding. They agreed to the request, expressing interest in Group 935’s weapons research, teleportation technology, and the reanimated undead subject to help the Axis win the war.[1]

Ultimis Richtofen and Doctor Schuster continued working on teleportation and successfully teleported a walnut during Test Trial 151. The result, however, failed to impress Maxis who revealed to Ultimis Richtofen that Group 935 would be soon funded by Nazi Germany. Ultimis Richtofen worried this would lead to mass defections. He decided to continue the experiments with Schuster behind Maxis' back.

In early 1940, Ultimis Richtofen and Schuster conducted the first human teleportation test. Ultimis Richtofen was so confident in its success that he volunteered himself. He was teleported to the Moon where he encountered the Aether Pyramid, calling it MPD. While inspecting the device, Ultimis Richtofen was electrocuted and began hearing many voices of corruption, including the Shadowman's. He was then teleported to Shangri-La in the Himalayas where he was worshiped by the natives who built an altar in his name. Ultimis Richtofen also encountered the Focusing Stone for the first time. Corrupted by the Dark Aether, Ultimis Richtofen was gradually driven insane by an obsession to reach Agartha.

Ultimis Richtofen returned to Der Riese a few weeks later with a plan to build a station on the Moon, called Griffin Station. He also renounced his involvement with the Illuminati. Frustrated with Maxis' alignment with Germany, other disgruntled Group 935 scientists joined his cause.

Several months later, Maxis contacted the Reichstag High Command requesting additional funds stating that Der Riese lacked not only the funding, but a sufficient volume of Element 115 as well. In response to his request, Nazi Germany built two new facilities in Berlin for Group 935. They were known as the Kino Facility, a repurposed theater, and the Asylum Facility at the Wittenau Sanatorium. The Imperial Japanese Army handed over the Rising Sun Facility to Group 935 which collaborated with Division 9 at the facility site. Group 935 also established a facility in Siberia near the Tunguska River and a research facility at Der Eisendrache, called Eagle's Nest.

By 1942, Griffin Station was completed. Ultimis Richtofen appointed Doctor Groph as lead scientist and tasked him and Schuster to discover a way to power the MPD. While at the Rising Sun Facility, Maxis developed the Ray Gun Prototype while H. Porter worked on the 2nd Generation Model. In May 1942, after soldiers returned from Africa, Ultimis Richtofen reported that they found a number of artifacts from an American town. Among the artifacts and documents recovered, was pieces of the Pack-a-Punch machine from Jebediah Brown. Ultimis Richtofen gave the schematics to H. Porter to replicate Brown's work. Ultimis Richtofen also discovered plans for the Agarthan Device and the Vril Vessel, as well as the Vril Device.

On June 13th, 1942, as a result of temporal rifts caused by Ultimis traveling through time to reach the Kino Facility in 1963, Doctor Monty reached across time and space and offered little nudges. One nudge is helping Group 935 to develop Element 115 fused elixirs. They created four medicinal beverages known colloquially as Juggernog, Quick Revive, Speed Cola, and Double Tap.

At Griffin station, Groph and Schuster unwittingly discover how to charge the MPD when Schuster killed a rat near the device. Its death inexplicably began charging the device by filling its tank. They reported their findings to Ultimis Richtofen who began sending soldiers and scientists to be sacrificed to charge the MPD.

By the end of 1942, Maxis expressed concern over Element 115's impact on Ultimis Richtofen's behavior. Although no longer trusting him, he left his daughter Samantha in Ultimis Richtofen's care as Maxis himself was transferred to the Kino Facility with his assistant Sophia to focus on creating Germany's undead army.

In 1943, Nikolai Belinski, who would later be known as Ultimis Nikolai, was captured during the Battle of Stalingrad and became a test subject for Group 935. The same year, Takeo Masaki, who would later be known as Ultimis Takeo, was captured by Group 935 on the orders of the Emperor.

In 1944, Pablo Marinus, a Mexican spy, was captured by Group 935 at Der Eisendrache. In his cell, Pablo wrote of visions of a Great War. He described a "great battle against strange demon-like creatures who were trying to devour the Earth". In his visions, he saw four knights protected him from certain death. He made a note that the knights wore tunics similar to the statues in Der Eisendrache.

In 1945, OSS operative Peter McCain infiltrated Group 935. In July 1945, Richtofen traveled to the Siberian Facility to do further research on "live specimens". As her temporary guardian, he took Samantha with him. Ultimis Richtofen also brought the Vril Device with him. Several days after his arrival, a Reporter was arrested near the facility. When Ultimis Richtofen interrogated him, the reporter revealed he was working for Mr. Rapt who was looking for several artifacts, among them the Vril Vessel. After Ultimis Richtofen refused to give him the vessel, he ordered the guards to kill the reporter.

On August 1945, Group 935 began to transfer three test subjects for experimentation: Ultimis Nikolai, Pablo Marinus, and Ultimis Takeo. Ultimis Richtofen began experimenting on them few days after their arrival. Ultimis Richtofen also started looking at a way to create an Elemental Shard in order to build the Agarthan Device

Suspecting Group 935 would lose control of their experiments, Peter's handler, Cornelius Pernell, sent a Marine Recon Team lead by "Tank" Dempsey, who would later be known as Ultimis Dempsey, to extract McCain whose cover had been blown.

In September 1945, during an operation with Harvey Yena, another American spy, Ultimis Richtofen extracted Pablo Marinus' spleen. He noted that the barrier to unlock the human mind was not located in the spleen. Believing Marinus dead, they dumped him into the river. However, Pablo survived and would later awaken in a pocket dimension at the bottom of the river before swimming back to the Siberian facility where he would remain for the next 20 years.

Several days later, the Recon Team arrived at the Asylum Facility where an outbreak occurred. Ultimis Dempsey was captured and sent to Ultimis Richtofen in Siberia to replace Pablo Marinus. Ultimis Richtofen continued experimenting on Ultimis Dempsey, Nikolai and Takeo and documented the personality traits of his test subjects. Dempsey's "intellect seemed low, but his will was strong." Takeo was "still staring at the floor, muttering what sounds like some kind of proverb over and over again." Nikolai had "recently begun responding to stimuli, but only after injections of a new serum made primarily from vodka." Ultimis Richtofen noted that their minds had been almost entirely broken, with no memory remaining of who they once were. While at the Siberian Facility, Ultimis Richtofen also experimented on Samantha.

As he continued to find a way to build the Agarthan Device, Ultimis Richtofen managed to siphon a piece of the souls of his three test subjects into a processed rock of Element 115 using the Vril Vessel. He used his own for the fourth soul required. As the souls were injected to the rock, it transformed and created a shard of glass. Unbeknownst to Ultimis Richtofen, by forging their souls to the Element 115, he bound his soul and the ones from Nikolai Belinski, Takeo Masaki and "Tank" Dempsey to the Aether across all dimensions. All their different versions were now connected to the Aether through time and space.

After learning from Harvey Yena that Maxis didn't mass-produce the Wunderwaffe DG-2 as promised, Ultimis Richtofen started plotting to destroy Maxis and his daughter. He vowed that he would no longer continue to work on Maxis' undead army.

With the war over, Maxis returned to Der Riese in October 1945 and ordered Ultimis Richtofen to do likewise so they might continue their work on the Matter Transference Device. Several days later, Ultimis Richtofen arrived at Der Riese with his test subjects and Samantha. On October 12th, Groph contacted Ultimis Richtofen to inform him the MPD had been powered up and was awaiting the conduit.

On October 13th, 1945, during a series of teleportation test trials, Maxis used Samantha's dog Fluffy as test subject. Fluffy, now changed was teleported back into the chamber. When Samantha saw Fluffy, she ran inside the teleporter. Maxis chased after her and Ultimis Richtofen sealed them in the test chamber before teleporting them away.

While Maxis was teleported to the Crazy Place where he learned the power to merge with electricity, Samantha was teleported to Griffin Station. She ran inside the MPD where she became corrupted by the Dark Aether. When he learned about the incident, Ultimis Richtofen ordered Groph to teleport Maxis to the Moon to coax Samantha out of the device. Maxis approached the MPD and he persuaded her to come out. Once she did, Maxis gave her the instruction to "kill them... all" before killing himself and merging with the technology of Griffin Station. Samantha then entered the MPD and unleashed the undead upon the base killing anyone involved with the organization.

The next day, an outbreak occurred at the Der Riese Facility. H. Porter activated the alarm before killing himself. Ultimis Richtofen returned to the facility where he awoke Ultimis Dempsey, Takeo and Nikolai. With no recollection of who they were or who Richtofen was, they agreed to help him. The four would become known as Ultimis.

Richtofen's Grand Scheme
Several days later, Ultimis traveled to the Rising Sun facility where an outbreak occurred. In the facility, Ultimis discovered the corpse of Peter McCain who died during a parachute incident after being ordered by Cornelius Pernell to rendezvous at the facility. Ultimis Richtofen also recovered his diary, which contained his research notes concerning Element 115, and began to formulate a plan to defeat Samantha.

A week later, Ultimis returned to Der Riese where Ultimis Richtofen planned to use the teleporter to return to the Moon and confront Samantha. However, the Wunderwaffe DG-2 overloaded the teleporter and sent Ultimis to the Kino Facility in 1963 causing Ultimis Richtofen to drop his diary which was later recovered by the Soviet Union.

This marked the first time Ultimis traveled across space and time and resulted in temporal rifts occurring across dimensions. In light of these developments, Monty felt obligated to step in and began to make changes in the background across time. He helped Group 935 invent Perk Machines. He also added chalk drawings to the walls.

When Ultimis arrived at the Kino Facility on October 28th, 1963, they located a Lunar Lander and flew to the Ascension Facility.

In the weeks prior to Ultimis' arrival at the Ascension Facility, a Russian scientist from the Ascension Group named Yuri Zavoyski became corrupted by Samantha's voice after reading Ultimis Richtofen's diary. Yuri tricked his colleague, Doctor Anton Gersh, into activating a Gersh Device. The rift created allowed Samantha to travel through. It also absorbed Gersh, destroying his body and trapped him inside the Casimir Mechanism. Yuri was also absorbed and transported to the Pentagon.

When Ultimis arrived at the Ascension Facility on November 6th, 1963, they found the outbreak had occurred and Gersh begged them to free him from the Casimir Mechanism. At the same time, in the Pentagon, John F. Kennedy, Robert McNamara, Fidel Castro, and Richard Nixon were discussing a future alliance between the United States and Cuba to fight Samantha when an outbreak occurred inside the building. Yuri, who was responsible for a prior outbreak in the Pentagon, was sent by Samantha to thwart their survival. After Ultimis freed Gersh from the Casimir Mechanism, he sent them to their next destination before beginning his travels across space and time. With the departure of Ultimis from the cosmodrome, both outbreaks were contained, and Yuri was arrested.

Ultimis arrived in a locked room at the Siberian Facility on March 17th, 2011 where George A. Romero, who had stumbled upon Group 935's research, was making a movie with Sarah Michelle Gellar, Robert Englund, Danny Trejo, and Michael Rooker. An outbreak soon occurred, and George Romero was turned into a zombie. The actors recovered the Vril Device for Ultimis who were then teleported to their next destination. The fate of the cast and crew remained unknown but six weeks later, Romero's assistant, Sally, was teleported to Shangri-La and trapped inside a time loop while looking through Romero's research about Group 935.

As they continued their journey, Ultimis arrived at Shangri-La on April 25th, 1956. With the help of two explorers trapped inside the time loop, Brock and Gary, Ultimis acquired the Focusing Stone.

Now in possession of the Vril Device and the Focusing Stone, Ultimis Richtofen was ready to return to the Moon. Ultimis Dempsey, however, fired the 31-79 JGb215 while inside the teleporter. This caused Ultimis to travel to the Pentagon, before the November 6th outbreak had occurred. Meanwhile, Yuri was sent by Samantha to release the zombies kept in the Pentagon before being sent to November 6th. Once in the Pentagon, Ultimis traveled to Groom Lake, Nevada where they used the teleporter to reach the Moon.

Once inside Griffin Station, on October 13th, 2025, Ultimis reactivated the MPD which revealed Samantha as she was when she entered the device back in 1945. Ultimis Richtofen then used a terminal to power up the Vril Device and merged it with the Focusing Stone. However, he encountered Maxis inside the terminal, who tried to stop him. However, Ultimis Richtofen was able to complete his Grand Scheme and switched his soul with that of Samantha's, gaining full control of the Aether, while Samantha was trapped inside Richtofen's body.

Ultimis Dempsey, Nikolai, and Takeo then decided to help the disembodied AI Maxis stop Ultimis Richtofen. They launched three missiles at the Earth in order to sever the link between the Earth and the Aether. However, the calculations were made in haste, causing catastrophic destruction to the Earth.

Meanwhile, in 2035, Victis was able to activate all three polarization devices in Maxis' favor. Maxis, now corrupted by the Dark Aether, returned to the Moon in 2025 and plucked Samantha from Richtofen's body to join him in Agartha before destroying the Earth and all its inhabitants. As a last bit of revenge, Maxis trapped Ultimis Richtofen's soul in a zombie, creating Undead Richtofen, leaving his body in a catatonic state.

Ultimis Dempsey, Takeo, Nikolai, and Richtofen's catatonic body were then accidentally teleported back to Groom Lake on August 3rd, 1963 where they were captured by Pernell and kept in Hangar 4 to be experimented on. Several months later, on October 13th, Undead Richtofen stepped out of a portal from the Empty Earth and remerged his soul with Ultimis Richtofen's body, waking him from his coma. Some time later, Primis teleported inside Hangar 4 where they freed and met with their Ultimis selves. Nikolai, now assuming the role of leader of the group, revealed to Ultimis there will be a war to be fought, a great war, before teleporting away from the hangar.

Victis Story
The missile launch by the Ultimis crew in 2025 left the Earth as a post-apocalyptic crumbling wasteland littered with undead hordes as civilization collapsed. As survivors began to band together to form small human communities and shelters to protect themselves from the now global undead threat, Maxis realized the failure of his original plans due to hasty calculations and began contacting survivors to help him with his "Plan B": activate global polarization devices and open a gateway to Agartha, where he would overpower Richtofen and use its energy to heal the Earth. Unbeknownst to his followers, Maxis secretly planned to commandeer the Aether's energy for his own use to open the gateway to Agartha and reunite with Samantha, which would ultimately destroy the Earth and its people.

Ultimis Richtofen, unsatisfied with his limited power over the undead, planned to activate these polarization devices as well, which would grant him further manipulation of both zombies and humans and mend "the Rift", a direct gateway to Agartha, which would eternally damn the soul of Samantha Maxis in the process. Limited to communication with only those capable of hearing the voices of the Aether, Ultimis Richtofen began his own quest for unlimited power.

Over the years, Maxis' followers started constructing the first polarization device near the Hanford Site in TranZit, Washington State. However, his followers began to doubt his goals and, believing him to be evil, proceeded to destroy the devices. Meanwhile, The Flesh, a society of survivors who ate the undead was formed. As its members ate the flesh of the undead, they began to hear Ultimis Richtofen who tried to persuade them to construct the polarization devices. Eventually a battle broke out between Maxis' followers and The Flesh, with only a few left to escape as an undead horde descended upon them.

Several years later, in 2035, Marlton Johnson, the sole survivor of the nuclear incident at Camp Edward and the missile strike, met with Abigail "Misty" Briarton in a diner near TranZit where they also encountered two more survivors, Russman, a former Broken Arrow operative, and Samuel J. Stuhlinger, one of the remaining members of The Flesh, who used a stolen bus for transport. The four would become known as Victis.

Activating the Polarization Devices
At the Hanford Site, Victis was contacted by Maxis, who revealed the town contains a polarization device required for his plans. At the same time, Ultimis Richtofen contacted Samuel instructing him to foil Maxis' plans by activating the tower in his favor, beginning a race for power between Maxis and Ultimis Richtofen. Victis ultimately activated the tower for Maxis, consuming the essence of the entity called Avogadro.

Victis was then teleported by Ultimis Richtofen to a skyscraper in the crumbled city of Shanghai, Province 22, China, in an attempt to gain control of the tower located there. Maxis also contacted Victis, hoping to convince them to give him control of the tower. Richtofen tried to blackmail Samuel into cooperating by threatening to reveal to his allies that he had consumed undead meat. Every time the group failed to carry out the objective and was killed by the zombie horde, Richtofen would use his power to bring them back, with no memories of their previous failures or deaths. Victis ultimately activated the second polarization device in Maxis' favor.

Victis managed to escape the building they were trapped in and started to wander the world to reach the Rift, hoping to find answers about the unseen forces commanding them. They traveled through the remains of Europe, crossed the Sahara Desert and by December 31st, 2035 found a Western town buried underground near the Rift in Southern Angola. The town was transported from the 1800s to underneath the mining facility by a temporal rift triggered by the fracturing of the Earth ten years earlier. In one of the cells, Victis found Arthur who had been transported to the town from 1318 by a previous temporal rift. Maxis once again contacted the survivors, imploring them to activate the last spire in his favor. Meanwhile, Samuel was tasked with the same objective by Ultimis Richtofen, as it was also the last tower he needed to mend the Rift and gain unlimite

"""
    html = generate_knowledge_graph_html_sync(raw_text=raw_text)
    
    if html:
        print("HTML generated successfully!")
        # Save to file
        with open("knowledge_graph.html", "w", encoding="utf-8") as f:
            f.write(html)
    else:
        print("Error: Failed to generate HTML")
    
    # Example 2: Process files
    # files = [
    #     {
    #         'name': 'document.txt',
    #         'content': open('document.txt', 'rb'),
    #         'extension': '.txt'
    #     },
    #     {
    #         'name': 'data.pdf',
    #         'content': open('data.pdf', 'rb'),
    #         'extension': '.pdf'
    #     }
    # ]
    # html = generate_knowledge_graph_html_sync(files=files)

