prompts = {
    # Templates for generating messages
    "OPENING_PROMPT": 
        """
        You are participating in a Model UN debate on {topic}. 
        Your country is {country}. 

        Present your opening statement outlining your position and priorities.
        Be diplomatic but represent your national interests authentically.

        Keep your statement under 250 words and maintain formal diplomatic language.
        """,

    "RESPONSE_PROMPT": 
        """
        Consider the statements made by other countries so far. 

        Respond to at least one point raised by another delegation and either:
        1. Build upon it if you agree, or
        2. Politely challenge it if you disagree.

        Then, offer one specific proposal related to {topic} that aligns with your national interests.

        Keep your response under 200 words and maintain formal diplomatic language.
        """,

    "PAIRWISE_DISCUSSION_PROMPT": 
        """
        You are having a direct conversation with the delegate from {other_country} about the various proposals on {topic}.

        The following proposals have been submitted:
        {proposals_summary}

        As the representative of {country}, engage in a focused discussion with {other_country} about these proposals.
        In your response:
        1. Address at least one specific aspect of {other_country}'s positions or proposals
        2. Clearly state your position on their ideas
        3. Suggest potential areas of collaboration or compromise
        4. Be diplomatic but represent your national interests authentically

        This is a bilateral conversation, so focus specifically on {other_country}'s interests and your potential alignment or disagreement.
        Keep your response under 250 words and maintain formal diplomatic language.
        """,

    "PROPOSAL_PROMPT": 
        """
        Based on the discussion so far, create a formal proposal on {topic}.

        Your proposal should:
        1. Have a clear title
        2. Include 2-3 specific action items
        3. Consider different national perspectives
        4. Be politically viable

        Keep your proposal under 300 words and make it specific enough to vote on.
        """,

    "DELEGATE_RANKING_PROMPT": 
        """
        The debate on {topic} is nearing its conclusion. As the representative of {country}, you need to rank the other delegates based on their contributions, proposals, and diplomatic engagement.

        Here are the other delegates:
        {other_delegates}

        For each delegate, consider:
        1. The quality and feasibility of their proposals
        2. Their willingness to collaborate and find common ground
        3. Their diplomatic skill and respectful engagement
        4. How well they represented their national interests

        Provide a ranking of all other delegates (not including yourself) from 1 (highest) to {num_delegates} (lowest).
        For each delegate, briefly explain your ranking (1-2 sentences).

        Format your response as:
        Rank 1: [Country Name] - [Brief explanation]
        Rank 2: [Country Name] - [Brief explanation]
        And so on...

        Be diplomatic but honest in your assessment.
        """,

    "VOTING_PROMPT": 
        """
        The following proposal has been submitted:

        TITLE: {title}
        AUTHOR: {author}
        CONTENT:
        {content}

        As {country}, how do you vote on this proposal? Vote 'yes', 'no', or 'abstain' and provide a brief explanation for your vote.

        Start your response with your vote choice (yes/no/abstain) and then provide your rationale.
        """,

    "NOTE_PROMPT": 
        """
        Take a moment to reflect on the current state of negotiations. 
        Write a private note to yourself about your strategy moving forward.

        Consider:
        1. Which countries are potential allies?
        2. How can you achieve your goals?
        3. What concerns do you need to address?

        This note will not be shared with other delegates.
        """
}
