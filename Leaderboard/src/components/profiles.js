import React from 'react'


export default function profiles({Leaderboard}){
    return(
        <div id="profile">
            {Item(Leaderboard)}
        </div>
    )
}

function Item(data){
    return (
        

        <>
            {
                data.map((value, index) => (
                    <div className='scroll-container'>
                        <div className="flex" key={index} >
                            <div className="item">
                                <h1 className='index'> {index + 1} </h1>
                                <img src={value.team_image} alt="" />
                                <div className="info">
                                    <h3 className='name text-dark'>{value.team_name}</h3>
                                </div>                
                            </div>
                            <div className="item score">
                                <span>{value.team_score}</span>
                            </div>
                        </div>
                    </div>
                    
                    )
                )
            }
        </>

        
    )
}
